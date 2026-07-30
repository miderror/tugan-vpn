from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table

ID = "2026-07-30T13:52:56:462758"
VERSION = "1.35.0"
DESCRIPTION = "add_register_or_get_user_function"


class RawTable(Table):
    pass

DROP_FUNCTION = """
DROP FUNCTION IF EXISTS register_or_get_user(
    BIGINT, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, BIGINT, INT, INT
) CASCADE;
"""

CREATE_FUNCTION = """
CREATE OR REPLACE FUNCTION register_or_get_user(
    p_tg_id BIGINT,
    p_username VARCHAR,
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_language_code VARCHAR,
    p_utm_source VARCHAR,
    p_referrer_id BIGINT,
    p_trial_days INT,
    p_ref_reward_days INT
) RETURNS TABLE (
    referral_processed BOOLEAN
) AS $$
DECLARE
    v_referral_processed BOOLEAN := FALSE;
    v_sub_id VARCHAR;
    v_client_id VARCHAR;
    v_access_token VARCHAR;
    v_email VARCHAR;
BEGIN
    IF EXISTS(SELECT 1 FROM core_user WHERE tg_id = p_tg_id) THEN
        UPDATE core_user 
        SET username = p_username, 
            first_name = p_first_name,
            last_name = p_last_name,
            language_code = p_language_code,
            updated_at = CURRENT_TIMESTAMP
        WHERE tg_id = p_tg_id 
          AND (username IS DISTINCT FROM p_username 
            OR first_name IS DISTINCT FROM p_first_name
            OR last_name IS DISTINCT FROM p_last_name
            OR language_code IS DISTINCT FROM p_language_code);

        referral_processed := FALSE;
        RETURN NEXT;
        RETURN;
    END IF;

    v_sub_id := replace(gen_random_uuid()::text, '-', '');
    v_client_id := gen_random_uuid()::text;
    v_access_token := encode(sha256(gen_random_uuid()::text::bytea), 'hex');
    v_email := replace(gen_random_uuid()::text, '-', '') || p_tg_id;

    INSERT INTO core_user (
        tg_id, username, first_name, last_name, language_code, utm_source, 
        email, sub_id, client_id, access_token, 
        expiry_date, next_reset_date, used_bytes, is_active_vpn, created_at, updated_at
    ) VALUES (
        p_tg_id, p_username, p_first_name, p_last_name, p_language_code, p_utm_source,
        v_email, v_sub_id, v_client_id, v_access_token,
        CURRENT_TIMESTAMP + (p_trial_days * INTERVAL '1 day'),
        NULL, 0, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    )
    ON CONFLICT (tg_id) DO NOTHING;

    IF p_referrer_id IS NOT NULL AND p_referrer_id <> p_tg_id THEN
        IF EXISTS(SELECT 1 FROM core_user WHERE core_user.tg_id = p_referrer_id) THEN
            INSERT INTO core_referral (referred_id, referrer_id)
            VALUES (p_tg_id, p_referrer_id)
            ON CONFLICT (referred_id) DO NOTHING;
            
            IF FOUND THEN
                UPDATE core_user 
                SET expiry_date = expiry_date + (p_ref_reward_days || ' days')::INTERVAL 
                WHERE core_user.tg_id = p_referrer_id;
                v_referral_processed := TRUE;
            END IF;
        END IF;
    END IF;

    referral_processed := v_referral_processed;
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;
"""


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="db", description=DESCRIPTION)

    async def run():
        await RawTable.raw(DROP_FUNCTION)
        await RawTable.raw(CREATE_FUNCTION)

    manager.add_raw(run)

    return manager

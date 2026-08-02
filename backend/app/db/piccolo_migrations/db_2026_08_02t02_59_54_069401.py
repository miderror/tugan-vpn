from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table

ID = "2026-08-02T02:59:54:069401"
VERSION = "1.35.0"
DESCRIPTION = "manual_migration"


class RawTable(Table):
    pass


DROP_FUNCTION = """
DROP FUNCTION IF EXISTS process_yookassa_payment(VARCHAR, BIGINT, INT) CASCADE;
"""

CREATE_FUNCTION = """
CREATE OR REPLACE FUNCTION process_yookassa_payment(
    p_payment_id VARCHAR,
    p_tg_id BIGINT,
    p_tariff_id INT
) RETURNS TABLE (
    success BOOLEAN,
    amount_str VARCHAR,
    tariff_name VARCHAR,
    username VARCHAR
) AS $$
DECLARE
    v_price NUMERIC(10, 2);
    v_duration_days INT;
    v_display_name VARCHAR;
    v_username VARCHAR;
BEGIN
    SELECT price, duration_days, display_name 
    INTO v_price, v_duration_days, v_display_name
    FROM core_tariff 
    WHERE id = p_tariff_id AND is_active = TRUE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL::VARCHAR, NULL::VARCHAR, NULL::VARCHAR;
        RETURN;
    END IF;

    INSERT INTO core_payment (payment_id, tg_id, tariff_id, amount, created_at)
    VALUES (p_payment_id, p_tg_id, p_tariff_id, v_price, CURRENT_TIMESTAMP)
    ON CONFLICT (payment_id) DO NOTHING;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL::VARCHAR, NULL::VARCHAR, NULL::VARCHAR;
        RETURN;
    END IF;

    UPDATE core_user
    SET expiry_date = GREATEST(expiry_date, CURRENT_TIMESTAMP) + (v_duration_days * INTERVAL '1 day'),
        is_active_vpn = TRUE,
        updated_at = CURRENT_TIMESTAMP
    WHERE tg_id = p_tg_id
    RETURNING COALESCE(core_user.username, '') INTO v_username;

    RETURN QUERY SELECT TRUE, v_price::VARCHAR, v_display_name, v_username;
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

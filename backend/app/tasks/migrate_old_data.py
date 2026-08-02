import asyncio
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

db_engine = engine_finder()
BATCH_SIZE = 500


def parse_iso_dt(dt_str: str | None) -> datetime:
    if not dt_str:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def execute_batch_insert(query_template: str, rows: list[tuple]):
    if not rows:
        return
    col_count = len(rows[0])
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        placeholders = []
        params = []
        for row in batch:
            placeholders.append(f"({', '.join(['{}'] * col_count)})")
            params.extend(row)

        sql = query_template.format(values=", ".join(placeholders))
        await db_engine.run_querystring(QueryString(sql, *params))


async def run_migration(json_file_path: str):
    print(f"[+] Чтение дампа {json_file_path}...")
    with open(json_file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    users_dict = {}
    keys_dict = {}
    referrals_list = []
    tariffs_dict = {}
    payments_list = []
    notifications_list = []

    for item in raw_data:
        model = item.get("model", "")
        pk = item.get("pk")
        fields = item.get("fields", {})

        if model.endswith(".user"):
            users_dict[pk] = fields
        elif model.endswith(".key"):
            user_id = fields.get("user")
            keys_dict[user_id] = fields
        elif model.endswith(".referral"):
            ref_id = item.get("pk") or fields.get("referred_user") or fields.get("referred_user_id")
            referrer_id = fields.get("referrer_user") or fields.get("referrer_user_id") or fields.get("referrer_id")
            if ref_id and referrer_id:
                referrals_list.append((int(ref_id), int(referrer_id)))
        elif model.endswith(".tariff"):
            tariffs_dict[pk] = fields
        elif model.endswith(".payment"):
            payments_list.append((pk, fields))
        elif model.endswith(".notification"):
            notifications_list.append(fields)

    print(
        f"[+] Загружено из дампа: {len(users_dict)} юзеров, {len(keys_dict)} ключей, {len(payments_list)} платежей."
    )

    print("[+] Миграция тарифов (core_tariff)...")
    tariff_rows = []
    for pk, t in tariffs_dict.items():
        tariff_rows.append(
            (
                pk,
                t.get("duration", "Тариф"),
                t.get("period_days", 30),
                f"{float(t.get('total', t.get('price', 0))):.2f}",
                f"{float(t.get('original_price')):.2f}"
                if t.get("original_price")
                else None,
                bool(t.get("is_bestseller", False)),
                True,
            )
        )
    if tariff_rows:
        sql = """
        INSERT INTO core_tariff (id, display_name, duration_days, price, original_price, is_bestseller, is_active)
        VALUES {values}
        ON CONFLICT (id) DO UPDATE SET display_name = EXCLUDED.display_name, price = EXCLUDED.price;
        """
        await execute_batch_insert(sql, tariff_rows)

    print("[+] Объединение User + Key -> core_user...")
    user_rows = []
    user_expiries = {}

    for tg_id, u in users_dict.items():
        key = keys_dict.get(tg_id)
        created_at = parse_iso_dt(u.get("created_at"))
        updated_at = parse_iso_dt(u.get("updated_at"))

        if key:
            email = key.get("email") or f"user_{tg_id}@tugan.vpn"
            sub_id = key.get("sub_id") or uuid.uuid4().hex
            client_id = key.get("client_id") or str(uuid.uuid4())
            access_token = (
                key.get("access_token")
                or hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
            )
            used_bytes = int(key.get("used_bytes", 0))
            is_active_vpn = bool(key.get("is_active", True))

            exp_ms = key.get("expiry_time")
            expiry_date = (
                datetime.fromtimestamp(exp_ms / 1000.0, tz=timezone.utc)
                if exp_ms
                else created_at
            )

            nr_str = key.get("next_reset_date")
            next_reset_date = parse_iso_dt(nr_str) if nr_str else None
            claimed_gift = not bool(key.get("can_claim_gift", True))
            tried_to_connect = bool(key.get("tried_to_connect", False))
        else:
            email = f"user_{tg_id}@tugan.vpn"
            sub_id = uuid.uuid4().hex
            client_id = str(uuid.uuid4())
            access_token = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
            used_bytes = 0
            is_active_vpn = True
            expiry_date = created_at
            next_reset_date = None
            claimed_gift = False
            tried_to_connect = False

        user_expiries[tg_id] = expiry_date
        user_rows.append(
            (
                tg_id,
                u.get("username") or "",
                u.get("first_name") or "",
                u.get("last_name") or "",
                u.get("language_code") or "ru",
                u.get("utm_source"),
                email,
                sub_id,
                client_id,
                access_token,
                used_bytes,
                is_active_vpn,
                expiry_date,
                next_reset_date,
                claimed_gift,
                tried_to_connect,
                created_at,
                updated_at,
            )
        )

    if user_rows:
        sql = """
        INSERT INTO core_user (
            tg_id, username, first_name, last_name, language_code, utm_source,
            email, sub_id, client_id, access_token, used_bytes, is_active_vpn,
            expiry_date, next_reset_date, claimed_gift, tried_to_connect, created_at, updated_at
        ) VALUES {values}
        ON CONFLICT (tg_id) DO NOTHING;
        """
        await execute_batch_insert(sql, user_rows)

    print("[+] Миграция рефералов (core_referral)...")
    referral_rows = [
        (int(ref_id), int(referrer_id))
        for ref_id, referrer_id in referrals_list
        if int(ref_id) in users_dict and int(referrer_id) in users_dict and int(ref_id) != int(referrer_id)
    ]
    if referral_rows:
        sql = """
        INSERT INTO core_referral (referred_id, referrer_id)
        VALUES {values}
        ON CONFLICT (referred_id) DO NOTHING;
        """
        await execute_batch_insert(sql, referral_rows)

    print("[+] Миграция платежей (core_payment)...")
    payment_rows = []
    default_tariff_id = next(iter(tariffs_dict.keys())) if tariffs_dict else 1

    for payment_id, p in payments_list:
        tg_id = p.get("user")
        if tg_id not in users_dict:
            continue
        created_at = parse_iso_dt(p.get("created_at"))
        amount_str = f"{float(p.get('amount', 0)):.2f}"

        payment_rows.append(
            (
                str(payment_id),
                tg_id,
                default_tariff_id,
                amount_str,
                created_at,
            )
        )

    if payment_rows:
        sql = """
        INSERT INTO core_payment (payment_id, tg_id, tariff_id, amount, created_at)
        VALUES {values}
        ON CONFLICT (payment_id) DO NOTHING;
        """
        await execute_batch_insert(sql, payment_rows)

    print("[+] Миграция и нормализация типов уведомлений (core_notification)...")
    notification_rows = []
    type_map = {
        "trial_activation_reminder": "trial_reminder",
        "trial_period_end": "trial_ended",
    }

    for n in notifications_list:
        tg_id = n.get("tg_id")
        if tg_id not in users_dict:
            continue

        raw_type = n.get("notification_type", "")
        created_at = parse_iso_dt(n.get("last_notification_time"))

        if raw_type in type_map:
            mapped_type = type_map[raw_type]
        elif raw_type == "subscription_expiry":
            exp_date = user_expiries.get(tg_id)
            if exp_date:
                epoch = int(exp_date.timestamp())
                mapped_type = f"sub_exp_{epoch}"
            else:
                continue
        else:
            mapped_type = raw_type

        notification_rows.append((tg_id, mapped_type, created_at))

    if notification_rows:
        sql = """
        INSERT INTO core_notification (tg_id, notification_type, created_at)
        VALUES {values};
        """
        await execute_batch_insert(sql, notification_rows)

    print("[SUCCESS] Все данные успешно импортированы!")


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "data_logic.json"
    asyncio.run(run_migration(file_path))

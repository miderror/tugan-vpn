import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone

from piccolo.engine import engine_finder
from piccolo.querystring import QueryString
from saq import Queue

from app.config.settings import settings

# IMPORT SAQ QUEUE (Укажите правильный путь к вашей очереди)
saq_queue = Queue.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
)

db_engine = engine_finder()

TRIAL_DAYS = 7
REFERRAL_DAYS = 14
THRESHOLD_SECONDS = 5 * 3600.0  # Порог 5 часов


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _fmt_dt(dt: datetime | None) -> str:
    if dt is None:
        return "None (Не задано)"
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


async def recalculate_user_subscriptions(
    clients_json_path: str = "clients.json", dry_run: bool = False
):
    print("[+] Fetching dataset from PostgreSQL...")

    users = await db_engine.run_querystring(
        QueryString(
            """
            SELECT tg_id, email, created_at, used_bytes, is_active_vpn, expiry_date, next_reset_date 
            FROM core_user
            """
        )
    )

    referrals = await db_engine.run_querystring(
        QueryString(
            """
            SELECT r.referrer_id, u.created_at AS ref_created_at
            FROM core_referral r
            JOIN core_user u ON r.referred_id = u.tg_id
            """
        )
    )

    payments = await db_engine.run_querystring(
        QueryString(
            """
            SELECT p.tg_id, p.created_at, t.duration_days
            FROM core_payment p
            JOIN core_tariff t ON p.tariff_id = t.id
            """
        )
    )

    # Загружаем данные с ноды из clients.json
    node_map: dict[str, int] = {}
    if os.path.exists(clients_json_path):
        with open(clients_json_path, "r", encoding="utf-8") as f:
            raw_clients = json.load(f)
            node_map = {
                c["email"]: c.get("expiryTime", 0) for c in raw_clients if "email" in c
            }

    # Собираем все события продлений
    user_events: dict[int, list[tuple[datetime, int]]] = {}

    for u in users:
        tg_id = u["tg_id"]
        c_at = _to_utc(u["created_at"])
        user_events[tg_id] = [(c_at, TRIAL_DAYS)]

    for r in referrals:
        referrer_id = r["referrer_id"]
        if referrer_id in user_events:
            user_events[referrer_id].append(
                (_to_utc(r["ref_created_at"]), REFERRAL_DAYS)
            )

    for p in payments:
        tg_id = p["tg_id"]
        if tg_id in user_events:
            user_events[tg_id].append((_to_utc(p["created_at"]), p["duration_days"]))

    now = datetime.now(timezone.utc)
    extended_users = []

    # Счетчики сравнения с нодой
    node_equal_count = 0
    node_lower_count = 0
    node_greater_count = 0
    node_missing_count = 0

    for u in users:
        tg_id = u["tg_id"]
        email = u["email"]
        events = user_events.get(tg_id, [])
        events.sort(key=lambda x: x[0])

        current_expiry: datetime | None = None
        for event_time, duration_days in events:
            if current_expiry is None or event_time > current_expiry:
                current_expiry = event_time + timedelta(days=duration_days)
            else:
                current_expiry = current_expiry + timedelta(days=duration_days)

        db_expiry = _to_utc(u["expiry_date"])

        # Условие: подписка продлена (> 5 часов разница) И дата окончания в будущем
        if not current_expiry or current_expiry <= now:
            continue

        if db_expiry is not None:
            time_gained_sec = (current_expiry - db_expiry).total_seconds()
        else:
            time_gained_sec = float("inf")

        if time_gained_sec > THRESHOLD_SECONDS:
            node_ts = node_map.get(email, 0)
            node_dt = (
                datetime.fromtimestamp(node_ts / 1000.0, tz=timezone.utc)
                if node_ts > 0
                else None
            )

            node_status = "НЕТ НА НОДЕ"
            final_expiry_to_apply = current_expiry

            if node_dt:
                diff_sec = (node_dt - current_expiry).total_seconds()
                if abs(diff_sec) <= THRESHOLD_SECONDS:
                    node_status = "РАВНО (==)"
                    node_equal_count += 1
                elif diff_sec < -THRESHOLD_SECONDS:
                    node_status = "НА НОДЕ МЕНЬШЕ (<)"
                    node_lower_count += 1
                else:
                    node_status = "НА НОДЕ БОЛЬШЕ (>)"
                    node_greater_count += 1
                    # ВОЗЬМЕМ ЗНАЧЕНИЕ С НОДЫ
                    final_expiry_to_apply = node_dt
            else:
                node_missing_count += 1

            extended_users.append(
                {
                    "tg_id": tg_id,
                    "email": email,
                    "db_expiry": db_expiry,
                    "recalc_expiry": current_expiry,
                    "node_expiry": node_dt,
                    "final_expiry": final_expiry_to_apply,
                    "node_status": node_status,
                }
            )

    # 1. ПОПОЛЬЗОВАТЕЛЬСКИЙ ВЫВОД
    print(
        f"\n================ УВЕЛИЧЕНА ПОДПИСКА (> 5 ч) [{len(extended_users)} чел.] ================"
    )
    for sample in extended_users:
        print(f"TG ID: {sample['tg_id']} | Email: {sample['email']}")
        print(f"  Было в БД:    {_fmt_dt(sample['db_expiry'])}")
        print(f"  Пересчитано:  {_fmt_dt(sample['recalc_expiry'])}")
        print(
            f"  На Ноде:      {_fmt_dt(sample['node_expiry'])}  [{sample['node_status']}]"
        )
        print(f"  -> ИТОГ В БД: {_fmt_dt(sample['final_expiry'])}")
        print("-" * 70)

    # 2. ИТОГОВАЯ СВОДКА
    print("\n================ ИТОГИ ПЕРЕСЧЕТА ================")
    print(f"Всего пользователей с продлением подписки (>5ч): {len(extended_users)}")
    print(f"  • На ноде РАВНО пересчету (diff <= 5h):        {node_equal_count}")
    print(f"  • На ноде МЕНЬШЕ чем пересчет (diff > 5h):     {node_lower_count}")
    print(f"  • На ноде БОЛЬШЕ чем пересчет (будет с ноды):  {node_greater_count}")
    if node_missing_count > 0:
        print(f"  • Отсутствуют на ноде / нет даты:             {node_missing_count}")
    print("=================================================\n")

    if dry_run:
        print("[!] Включен режим --dry-run. База данных и таски не затронуты.")
        return

    if not extended_users:
        print("[i] Нет пользователей для обновления.")
        return

    # 3. ПРИМЕНЕНИЕ ИЗМЕНЕНИЙ В БД
    print(f"[+] Обновляем {len(extended_users)} пользователей в PostgreSQL...")
    for u in extended_users:
        await db_engine.run_querystring(
            QueryString(
                """
                UPDATE core_user
                SET expiry_date = {}, updated_at = CURRENT_TIMESTAMP
                WHERE tg_id = {}
                """,
                u["final_expiry"],
                u["tg_id"],
            )
        )
    print("[SUCCESS] База данных успешно обновлена!")

    # # 4. ОТПРАВКА ТАСОК В ОЧЕРЕДЬ SAQ
    if saq_queue is not None:
        print("[+] Отправляем задачи в очереди SAQ (update_user_on_nodes_task)...")
        for u in extended_users:
            await saq_queue.enqueue("update_user_on_nodes_task", tg_id=u["tg_id"])
        print(f"[SUCCESS] Успешно отправлено {len(extended_users)} тасок в SAQ!")
    else:
        print(
            "[!] ОШИБКА: Объект saq_queue не найден/не импортирован. Задачи в очередь не отправлены!"
        )


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    path = "clients.json"
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            path = arg
    asyncio.run(recalculate_user_subscriptions(clients_json_path=path, dry_run=is_dry))

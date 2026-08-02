import logging
from typing import Any

from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

logger = logging.getLogger(__name__)
db_engine = engine_finder()


async def _mark_notifications_sent(tg_ids: list[int], notification_type: str) -> None:
    if not tg_ids:
        return

    await db_engine.run_querystring(
        QueryString(
            """
            INSERT INTO core_notification (tg_id, notification_type, created_at)
            SELECT unnest({}), {}, CURRENT_TIMESTAMP
            """,
            tg_ids,
            notification_type,
        )
    )


async def check_and_enqueue_periodic_notifications_task(ctx: dict[str, Any]) -> None:
    saq_queue = ctx.get("saq_queue")
    if not saq_queue:
        return

    trial_reminder_rows = await db_engine.run_querystring(
        QueryString(
            """
            SELECT u.tg_id 
            FROM core_user u
            WHERE u.tried_to_connect = FALSE 
              AND u.created_at <= CURRENT_TIMESTAMP - INTERVAL '5 hours'
              AND u.expiry_date > CURRENT_TIMESTAMP
              AND NOT EXISTS (
                  SELECT 1 FROM core_payment p WHERE p.tg_id = u.tg_id
              )
              AND NOT EXISTS (
                  SELECT 1 FROM core_notification n 
                  WHERE n.tg_id = u.tg_id AND n.notification_type = 'trial_reminder'
              )
            LIMIT 200
            """
        )
    )
    if trial_reminder_rows:
        tg_ids = [r["tg_id"] for r in trial_reminder_rows]
        await _mark_notifications_sent(tg_ids, "trial_reminder")
        for tg_id in tg_ids:
            await saq_queue.enqueue(
                "send_trial_activation_notification_task", user_id=tg_id
            )

    trial_end_rows = await db_engine.run_querystring(
        QueryString(
            """
            SELECT u.tg_id 
            FROM core_user u
            WHERE u.expiry_date <= CURRENT_TIMESTAMP
              AND NOT EXISTS (
                  SELECT 1 FROM core_payment p WHERE p.tg_id = u.tg_id
              )
              AND NOT EXISTS (
                  SELECT 1 FROM core_notification n 
                  WHERE n.tg_id = u.tg_id AND n.notification_type = 'trial_ended'
              )
            LIMIT 200
            """
        )
    )
    if trial_end_rows:
        tg_ids = [r["tg_id"] for r in trial_end_rows]
        await _mark_notifications_sent(tg_ids, "trial_ended")
        for tg_id in tg_ids:
            await saq_queue.enqueue(
                "send_trial_period_end_notification_task", user_id=tg_id
            )

    expiry_warning_rows = await db_engine.run_querystring(
        QueryString(
            """
            SELECT u.tg_id, 
                   EXTRACT(EPOCH FROM u.expiry_date)::BIGINT AS expiry_ts,
                   'sub_exp_' || EXTRACT(EPOCH FROM u.expiry_date)::BIGINT AS n_type
            FROM core_user u
            WHERE u.is_active_vpn = TRUE
              AND u.expiry_date > CURRENT_TIMESTAMP
              AND u.expiry_date <= CURRENT_TIMESTAMP + INTERVAL '24 hours'
              AND NOT EXISTS (
                  SELECT 1 FROM core_notification n 
                  WHERE n.tg_id = u.tg_id 
                    AND n.notification_type = ('sub_exp_' || EXTRACT(EPOCH FROM u.expiry_date)::BIGINT)
              )
            LIMIT 200
            """
        )
    )
    if expiry_warning_rows:
        type_to_ids: dict[str, list[int]] = {}
        for row in expiry_warning_rows:
            type_to_ids.setdefault(row["n_type"], []).append(row["tg_id"])

        for n_type, tg_ids in type_to_ids.items():
            await _mark_notifications_sent(tg_ids, n_type)

        for row in expiry_warning_rows:
            await saq_queue.enqueue(
                "send_subscription_expiry_notification_task",
                user_id=row["tg_id"],
                expiry_timestamp=row["expiry_ts"],
            )

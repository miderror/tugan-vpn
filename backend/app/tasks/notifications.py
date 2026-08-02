import time
from typing import Any

from app.config.settings import settings
from app.services.telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    _pluralize,
    send_telegram_message,
)


async def send_referral_notification_task(
    ctx: dict[str, Any], *, referrer_id: int, referred_username: str
) -> None:
    username = f"@{referred_username}" if referred_username else "без username"
    text = f"🎉 У вас новый реферал: {username}!\nВам начислено 100₽ на баланс."
    await send_telegram_message(ctx["http_client"], referrer_id, text)


async def send_subscription_expiry_notification_task(
    ctx: dict[str, Any], *, user_id: int, expiry_timestamp: int
) -> None:
    now = int(time.time())
    diff_seconds = max(0, expiry_timestamp - now)

    hours = diff_seconds // 3600
    minutes = (diff_seconds % 3600) // 60

    h_str = _pluralize(hours, "час", "часа", "часов")
    m_str = _pluralize(minutes, "минута", "минуты", "минут")

    text = (
        "⚠️ Срок действия подписки подходит к концу.\n"
        f"Осталось: <b>{h_str} {m_str}</b>.\n"
        "Оплатите, чтобы продлить её."
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    url=f"{settings.webapp_url}?startapp=subscription",
                )
            ]
        ]
    )
    await send_telegram_message(
        ctx["http_client"], user_id, text, reply_markup=markup, parse_mode="HTML"
    )


async def send_payment_success_notification_task(
    ctx: dict[str, Any], *, user_id: int, amount: str, tariff_name: str
) -> None:
    text = (
        "✅ Оплата прошла успешно!\n\n"
        f"💳 Сумма оплаты: <b>{amount} ₽</b>\n"
        f"⏳ Подписка продлена на: <b>{tariff_name}</b>\n\n"
        "Спасибо за покупку! 😊"
    )
    await send_telegram_message(ctx["http_client"], user_id, text, parse_mode="HTML")


async def send_admin_payment_notification_task(
    ctx: dict[str, Any],
    *,
    user_id: int,
    username: str,
    payment_id: str,
    amount: str,
    tariff_name: str,
) -> None:
    if not settings.admin_ids:
        return

    username_display = f"@{username}" if username else "без username"
    text = (
        "💰 <b>Новый платеж!</b>\n\n"
        f"👤 Пользователь: {username_display}\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"💰 Сумма: <b>{amount} ₽</b>\n"
        f"📅 Продление на: <b>{tariff_name}</b>\n"
        f"💳 Система оплаты: <b>yookassa</b>\n"
        f"🧾 ID платежа: <code>{payment_id}</code>\n\n"
        "📢 <i>Платеж успешно обработан!</i>"
    )

    http_client = ctx["http_client"]
    for admin_id in settings.admin_ids:
        await send_telegram_message(http_client, admin_id, text, parse_mode="HTML")


async def send_trial_activation_notification_task(
    ctx: dict[str, Any], *, user_id: int
) -> None:
    text = (
        "🎁 Вам начислено 7 бесплатных дней.\n"
        "Успейте ими воспользоваться, пока они активны."
    )
    await send_telegram_message(ctx["http_client"], user_id, text)


async def send_trial_period_end_notification_task(
    ctx: dict[str, Any], *, user_id: int
) -> None:
    text = (
        "⚠️ Ваш пробный период подошел к концу.\n\n"
        "Пожалуйста, продлите подписку, чтобы продолжить использование."
    )
    await send_telegram_message(ctx["http_client"], user_id, text)

from aiogram.exceptions import TelegramAPIError
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram import Bot, types
from django.conf import settings
from datetime import datetime, timedelta, timezone

bot = Bot(
    token=settings.TELEGRAM_SECRET_KEY,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

def pluralize(number: int, word_forms: tuple) -> str:
    remainder_10 = number % 10
    remainder_100 = number % 100

    if remainder_10 == 1 and remainder_100 != 11:
        return word_forms[0]
    elif 2 <= remainder_10 <= 4 and not (12 <= remainder_100 <= 14):
        return word_forms[1]
    return word_forms[2]

async def send_referral_notification(referrer_id: int, referred_username: str):
    try:
        print("Отправка уведомления о новом реферале")
        message_text = f"🎉 У вас новый реферал, username: @{referred_username}!\nВам начислено 100₽ на баланс"
        await bot.send_message(chat_id=referrer_id, text=message_text)
        print("успешно отправлено")
    except TelegramAPIError as e:
        print(f"Ошибка при отправке уведомления о реферале")

async def send_subscription_expiry_notification(user_id: int, expiry_time: int):
    try:
        expiry_datetime = datetime.fromtimestamp(expiry_time / 1000, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        time_difference = expiry_datetime - now
        
        hours = time_difference.seconds // 3600
        minutes = (time_difference.seconds % 3600) // 60
        
        hours_word = pluralize(hours, ("час", "часа", "часов"))
        minutes_word = pluralize(minutes, ("минута", "минуты", "минут"))
        
        time_left_str = f"{hours} {hours_word} {minutes} {minutes_word}"
        message_text = f"⚠️ Срок действия подписки подходит к концу.\nОсталось: {time_left_str}.\nОплатите, чтобы продлить её."
        builder = InlineKeyboardBuilder()
        builder.add(
            types.InlineKeyboardButton(text="Оплатить", url=f"{settings.WEBAPP_URL}?startapp=subscription")
        )
        await bot.send_message(chat_id=user_id, text=message_text, reply_markup=builder.as_markup())
    except TelegramAPIError as e:
        print(f"Ошибка при отправке уведомления о подписке: {e}")

async def send_payment_success_notification(user_id: int, amount: float, duration: str):
    try:
        print("Отправка уведомления об оплате")
        message_text = (
            f"✅ Оплата прошла успешно!\n\n"
            f"💳 Сумма оплаты: <b>{amount} ₽</b>\n"
            f"⏳ Подписка продлена на: <b>{duration}</b>\n\n"
            f"Спасибо за покупку! 😊"
        )

        await bot.send_message(chat_id=user_id, text=message_text)
        print("успешно отправлено")
    except TelegramAPIError as e:
        print(f"Ошибка при отправке уведомления об оплате: {e}")

async def send_admin_payment_notification(user_id: int, username: str, payment_id: str, amount: float, duration: str, payment_system: str):
    print("Отправка уведомления администраторам о новом платеже")

    username_display = f"@{username}" if username else "без username"

    message_text = (
        f"💰 <b>Новый платеж!</b>\n\n"
        f"👤 Пользователь: <b>{username_display}</b>\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"💰 Сумма: <b>{amount} ₽</b>\n"
        f"📅 Продление на: <b>{duration}</b>\n"
        f"💳 Система оплаты: <b>{payment_system}</b>\n"
        f"🧾 ID платежа: <code>{payment_id}</code>\n\n"
        f"📢 <i>Платеж успешно обработан!</i>"
    )

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=message_text)
            print(f"Уведомление отправлено админу {admin_id}")
        except TelegramAPIError as e:
            print(f"Ошибка при отправке уведомления админу {admin_id}: {e}")

async def send_trial_period_end_notification(user_id: int):
    try:
        message_text = (
            "⚠️ Ваш пробный период подошел к концу.\n\n"
            "Пожалуйста, продлите подписку, чтобы продолжить использование."
        )
        await bot.send_message(chat_id=user_id, text=message_text)
    except TelegramAPIError as e:
        print(f"Ошибка при отправке уведомления о завершении пробного периода: {e}")

async def send_trial_activation_notification(user_id: int):
    try:
        message_text = (
            "🎁 Вам начислено 7 бесплатных дней.\n"
            "Успейте ими воспользоваться, пока они активны"
        )
        await bot.send_message(chat_id=user_id, text=message_text)
    except TelegramAPIError as e:
        print(f"Ошибка при отправке уведомления-напоминания о пробном периоде: {e}")


from datetime import datetime, timedelta, timezone
import csv
from io import StringIO

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.models import User, Key, Referral, Payment
from django.db.models import Sum
from asgiref.sync import sync_to_async


panel_router = Router()


class UserEditorState(StatesGroup):
    waiting_for_message = State()


@panel_router.callback_query(F.data == "admin")
async def handle_admin_callback_query(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Статистика пользователей", callback_data="user_stats"))
    builder.row(InlineKeyboardButton(text="👥 Управление пользователями", callback_data="user_editor"))
    builder.row(InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="send_to_alls"))
    admin_panel_message = "🤖 Панель администратора"
    try:
        await callback_query.message.edit_text(admin_panel_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(admin_panel_message, reply_markup=builder.as_markup())
    await callback_query.answer()


@panel_router.message(Command("admin"))
async def handle_admin_message(message: types.Message, state: FSMContext):
    await state.clear()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Статистика пользователей", callback_data="user_stats"))
    builder.row(InlineKeyboardButton(text="👥 Управление пользователями", callback_data="user_editor"))
    builder.row(InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="send_to_alls"))
    await message.answer("🤖 Панель администратора", reply_markup=builder.as_markup())


@panel_router.callback_query(F.data == "user_stats")
async def user_stats_menu(callback_query: types.CallbackQuery):
    total_users = await sync_to_async(User.objects.count)()
    total_referrals = await sync_to_async(Referral.objects.count)()

    now = datetime.now(timezone.utc)
    total_payments_today = await sync_to_async(
        lambda: Payment.objects.filter(created_at__date=now.date()).aggregate(total=Sum('amount'))['total'] or 0
    )()

    total_payments_week = await sync_to_async(
        lambda: Payment.objects.filter(created_at__week=now.isocalendar()[1]).aggregate(total=Sum('amount'))['total'] or 0
    )()

    total_payments_all_time = await sync_to_async(
        lambda: Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    )()

    now_timestamp = int(now.timestamp() * 1000)
    paid_users = await sync_to_async(list)(Payment.objects.values_list('user__tg_id', flat=True).distinct())
    paid_users_set = set(paid_users)

    paid_keys_count = await sync_to_async(Key.objects.filter(user__tg_id__in=paid_users_set).count)()
    free_keys_count = await sync_to_async(Key.objects.exclude(user__tg_id__in=paid_users_set).count)()

    active_paid_keys = await sync_to_async(
        Key.objects.filter(user__tg_id__in=paid_users_set, expiry_time__gt=now_timestamp).count
    )()
    expired_paid_keys = paid_keys_count - active_paid_keys

    active_free_keys = await sync_to_async(
        Key.objects.exclude(user__tg_id__in=paid_users_set).filter(expiry_time__gt=now_timestamp).count
    )()
    expired_free_keys = free_keys_count - active_free_keys

    stats_message = (
        f"📊 <b>Подробная статистика проекта:</b>\n\n"
        f"👥 Пользователи:\n"
        f"   🌐 Зарегистрировано: <b>{total_users}</b>\n"
        f"   🤝 Привлеченных рефералов: <b>{total_referrals}</b>\n\n"
        f"🔑 Ключи:\n"
        f"   🌈 Всего сгенерировано: <b>{paid_keys_count + free_keys_count}</b>\n\n"
        f"   💳 Платно продлевавшиеся:\n"
        f"      ✅ Действующих: <b>{active_paid_keys}</b>\n"
        f"      ❌ Просроченных: <b>{expired_paid_keys}</b>\n\n"
        f"   🎁 Бесплатные ключи:\n"
        f"      ✅ Действующих: <b>{active_free_keys}</b>\n"
        f"      ❌ Просроченных: <b>{expired_free_keys}</b>\n\n"
        f"💰 Финансовая статистика:\n"
        f"   📅 За день: <b>{total_payments_today} ₽</b>\n"
        f"   📆 За неделю: <b>{total_payments_week} ₽</b>\n"
        f"   🏦 За все время: <b>{total_payments_all_time} ₽</b>\n"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Обновить", callback_data="user_stats"))
    builder.row(InlineKeyboardButton(text="📥 Выгрузить пользователей в CSV", callback_data="export_users_csv"))
    builder.row(InlineKeyboardButton(text="📥 Выгрузить оплаты в CSV", callback_data="export_payments_csv"))
    builder.row(InlineKeyboardButton(text="👑 Выгрузить платников в CSV", callback_data="export_paid_users_csv"))
    builder.row(InlineKeyboardButton(text="🔙 Вернуться в меню", callback_data="admin"))

    try:
        await callback_query.message.edit_text(stats_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(stats_message, reply_markup=builder.as_markup())
    await callback_query.answer()


@panel_router.callback_query(F.data == "send_to_alls")
async def handle_send_to_all(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin"))
    send_info_message = "✍️ Введите текст сообщения, который вы хотите отправить всем клиентам 📢🌐:"
    try:
        await callback_query.message.edit_text(send_info_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(send_info_message, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.waiting_for_message)
    await callback_query.answer()


@panel_router.message(UserEditorState.waiting_for_message)
async def process_message_to_all(message: types.Message, state: FSMContext):
    text_message = message.text

    try:
        users = await sync_to_async(list)(User.objects.all())
        total_users = len(users)
        success_count = 0
        error_count = 0

        for user in users:
            tg_id = user.tg_id
            try:
                await message.bot.send_message(chat_id=tg_id, text=text_message)
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"❌ Ошибка при отправке сообщения пользователю {tg_id}: {e}")

        await message.answer(
            f"📤 Рассылка завершена:\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"✅ Успешно отправлено: {success_count}\n"
            f"❌ Не доставлено: {error_count}"
        )
    except Exception as e:
        print(f"❗ Ошибка при подключении к базе данных: {e}")
    await handle_admin_message(message, state)


@panel_router.callback_query(F.data == "user_editor")
async def user_editor_menu(callback_query: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔍 Поиск по названию ключа",callback_data="search_by_key_name"))
    builder.row(InlineKeyboardButton(text="🆔 Поиск по Telegram ID", callback_data="search_by_tg_id"))
    builder.row(InlineKeyboardButton(text="🌐 Поиск по Username", callback_data="search_by_username"))
    builder.row(InlineKeyboardButton(text="🔗 Поиск по UTM-метке", callback_data="search_by_utm_source"))
    builder.row(InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="admin"))
    editor_menu_message = "👇 Выберите способ поиска пользователя:"
    try:
        await callback_query.message.edit_text(editor_menu_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(editor_menu_message, reply_markup=builder.as_markup())
    await callback_query.answer()


@panel_router.callback_query(F.data == "export_users_csv")
async def export_users_csv(callback_query: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_stats"))
    try:
        await callback_query.message.delete()
    except Exception as e:
        pass

    try:
        users = await sync_to_async(list)(User.objects.all())

        if not users:
            await callback_query.message.answer("📭 Нет пользователей для экспорта.", reply_markup=builder.as_markup())
            await callback_query.answer()
            return

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        
        header = [
            "tg_id", "username", "first_name", "last_name", "language_code",
            "is_bot", "activated_7_days", "tried_to_connect", "paid", "total_paid",
            "referrals_count", "referrer_user", "utm_source"
        ]
        csv_writer.writerow(header)
        for user in users:
            total_paid = await sync_to_async(
                lambda: Payment.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
            )()
            paid = total_paid != 0

            try:
                activated_7_days = await sync_to_async(
                    lambda: not Key.objects.filter(user=user).values_list('can_claim_gift', flat=True).first()
                )()
            except Exception:
                activated_7_days = False
            
            try:
                tried_to_connect = await sync_to_async(
                    lambda: Key.objects.filter(user=user).values_list('tried_to_connect', flat=True).first()
                )()
            except Exception:
                tried_to_connect = False

            referrals_count = await sync_to_async(
                lambda: Referral.objects.filter(referrer_user=user).count()
            )()

            referrer_username_or_id = ""
            try:
                referral = await sync_to_async(
                    lambda: Referral.objects.filter(referred_user=user).select_related('referrer_user').first()
                )()
                if referral:
                    referrer = referral.referrer_user
                    referrer_username_or_id = f"@{referrer.username}" if referrer.username else str(referrer.tg_id)
            except Exception as e:
                print(e)
            
            utm_source = user.utm_source or ""

            csv_writer.writerow([
                user.tg_id, user.username, user.first_name, user.last_name, user.language_code,
                user.is_bot, activated_7_days, tried_to_connect, paid, total_paid,
                referrals_count, referrer_username_or_id, utm_source
            ])

        csv_data.seek(0)
        file = BufferedInputFile(csv_data.getvalue().encode("utf-8-sig"), filename="users_export.csv")

        await callback_query.message.answer_document(
            file, caption="📥 Экспорт пользователей в CSV", reply_markup=builder.as_markup()
        )
        csv_data.close()
        await callback_query.answer()

    except Exception as e:
        print(f"Ошибка при экспорте пользователей в CSV: {e}")
        await callback_query.message.answer(
            "❗ Произошла ошибка при экспорте пользователей.", reply_markup=builder.as_markup()
        )
        await callback_query.answer()


@panel_router.callback_query(F.data == "export_payments_csv")
async def export_payments_csv(callback_query: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_stats"))
    try:
        await callback_query.message.delete()
    except Exception as e:
        pass

    try:
        payments = await sync_to_async(list)(Payment.objects.all().select_related('user'))

        if not payments:
            await callback_query.message.answer("📭 Нет платежей для экспорта.", reply_markup=builder.as_markup())
            await callback_query.answer()
            return

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        
        header = ["tg_id", "username", "first_name", "last_name", "amount", 
                 "payment_system", "status", "created_at_msk"]
        csv_writer.writerow(header)

        for payment in payments:
            user = payment.user
            created_at_msk = payment.created_at + timedelta(hours=3)
            csv_writer.writerow([
                user.tg_id, user.username, user.first_name, user.last_name,
                payment.amount, payment.payment_system, payment.status,
                created_at_msk.strftime("%d.%m.%Y %H:%M:%S")
            ])

        csv_data.seek(0)
        file = BufferedInputFile(csv_data.getvalue().encode("utf-8-sig"), filename="payments_export.csv")

        await callback_query.message.answer_document(
            file, caption="📥 Экспорт платежей в CSV", reply_markup=builder.as_markup()
        )
        csv_data.close()
        await callback_query.answer()

    except Exception as e:
        print(f"Ошибка при экспорте платежей в CSV: {e}")
        await callback_query.message.answer(
            "❗ Произошла ошибка при экспорте платежей.", reply_markup=builder.as_markup()
        )
        await callback_query.answer()


@panel_router.callback_query(F.data == "export_paid_users_csv")
async def export_all_paid_users_csv(callback_query: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_stats"))
    try:
        await callback_query.message.delete()
    except Exception as e:
        pass

    try:
        paid_users = await sync_to_async(list)(
            User.objects.filter(payment__isnull=False).prefetch_related('key_set').distinct()
        )

        if not paid_users:
            await callback_query.message.answer("📭 Нет платных пользователей для экспорта.", reply_markup=builder.as_markup())
            await callback_query.answer()
            return
        
        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)

        header = [
            "tg_id", "username", "first_name", "last_name", "total_paid", "expiry_time_msk",
        ]
        csv_writer.writerow(header)

        now_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

        for user in paid_users:
            key = await sync_to_async(lambda: user.key_set.first())()

            if key.expiry_time < now_timestamp:
                expiry_date_msk = "Неактивна"
            else:
                expiry_time_msk = datetime.fromtimestamp(key.expiry_time / 1000, tz=timezone.utc) + timedelta(hours=3)
                expiry_date_msk = expiry_time_msk.strftime("%d.%m.%Y %H:%M:%S")

            print(3.4)
            total_paid = await sync_to_async(
                lambda: Payment.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
            )()

            print(3.5)
            csv_writer.writerow([
                user.tg_id, user.username, user.first_name, user.last_name, total_paid, expiry_date_msk
            ])

        csv_data.seek(0)
        file = BufferedInputFile(csv_data.getvalue().encode("utf-8-sig"), filename="all_paid_users_export.csv")

        await callback_query.message.answer_document(
            file, caption="👑 Экспорт всех платных пользователей в CSV", reply_markup=builder.as_markup()
        )
        csv_data.close()
        await callback_query.answer()

    except Exception as e:
        print(f"Ошибка при экспорте платных пользователей в CSV: {e}")
        await callback_query.message.answer(
            "❗ Произошла ошибка при экспорте платных пользователей.", reply_markup=builder.as_markup()
        )
        await callback_query.answer()

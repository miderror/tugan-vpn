from datetime import datetime, timedelta, timezone
import csv
from io import StringIO

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api.models import User, Key, Referral, Payment
from django.db.models import Sum
from asgiref.sync import sync_to_async


editor_router = Router()


class UserEditorState(StatesGroup):
    waiting_for_tg_id = State()
    waiting_for_username = State()
    displaying_user_info = State()
    waiting_for_key_name = State()
    waiting_for_expiry_time = State()
    waiting_for_utm_source = State()


@editor_router.callback_query(F.data == "search_by_tg_id")
async def prompt_tg_id(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
    prompt_tg_id_message = "🔍 Введите Telegram ID клиента:"
    try:
        await callback_query.message.edit_text(prompt_tg_id_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(prompt_tg_id_message, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.waiting_for_tg_id)
    await callback_query.answer()


@editor_router.callback_query(F.data == "search_by_username")
async def prompt_username(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
    prompt_username_message = "🔍 Введите Username клиента:"
    try:
        await callback_query.message.edit_text(prompt_username_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(prompt_username_message, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.waiting_for_username)
    await callback_query.answer()

@editor_router.callback_query(F.data == "search_by_key_name")
async def prompt_key_name(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
    prompt_key_name_message = "🔑 Введите email ключа для поиска:"
    try:
        await callback_query.message.edit_text(prompt_key_name_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(prompt_key_name_message, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.waiting_for_key_name)
    await callback_query.answer()

@editor_router.callback_query(F.data == "search_by_utm_source")
async def prompt_utm_source(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
    prompt_utm_message = "🔗 Введите UTM-метку для поиска:"
    try:
        await callback_query.message.edit_text(prompt_utm_message, reply_markup=builder.as_markup())
    except Exception as e:
        await callback_query.message.answer(prompt_utm_message, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.waiting_for_utm_source)
    await callback_query.answer()

async def get_user_info(user: User, key: Key = None) -> str:
    tg_id = user.tg_id
    username = user.username
    referral_count = await sync_to_async(Referral.objects.filter(referrer_user=user).count)()

    if key is None:
        key = await sync_to_async(Key.objects.filter(user=user).first)()

    if key:
        expiry_date = key.expiry_date
        can_claim_gift_text = "не использован" if key.can_claim_gift else "использован"
        key_info = (
            f"🔑 Ключ: <code>{key.email}</code>\n"
            f"⏰ Дата истечения: <b>{expiry_date}</b>\n"
            f"🌐 Пробный период: <b>{can_claim_gift_text}</b>\n"
            f"🚀 Использовано трафика: <b>{key.used_gb} GB</b>\n"
            f"📈 Лимит: <b>{key.total_gb} GB</b>\n"
        )
    else:
        key_info = "🔑 Ключ: <b>отсутствует</b>\n"

    user_info = (
        f"📊 Информация о пользователе:\n\n"
        f"🆔 ID пользователя: <b>{tg_id}</b>\n"
        f"👤 Логин пользователя: <b>@{username}</b>\n"
        f"👥 Количество рефералов: <b>{referral_count}</b>\n\n"
        f"{key_info}"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📥 Выгрузить рефералов в CSV", callback_data=f"export_referrals_{tg_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
    return user_info, builder


@editor_router.message(UserEditorState.waiting_for_username)
async def handle_username_input(message: types.Message, state: FSMContext):
    username = message.text.strip()
    user = await sync_to_async(User.objects.filter(username=username).first)()

    if not user:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
        await message.answer("🔍 Пользователь с указанным username не найден. 🚫", reply_markup=builder.as_markup())
        await state.clear()
        return

    user_info, builder = await get_user_info(user)

    await message.answer(user_info, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.displaying_user_info)


@editor_router.message(UserEditorState.waiting_for_tg_id, F.text.isdigit())
async def handle_tg_id_input(message: types.Message, state: FSMContext):
    tg_id = int(message.text)
    user = await sync_to_async(User.objects.filter(tg_id=tg_id).first)()

    if not user:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
        await message.answer("❌ Пользователь с указанным tg_id не найден. 🔍", reply_markup=builder.as_markup())
        await state.clear()
        return

    user_info, builder = await get_user_info(user)

    await message.answer(user_info, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.displaying_user_info)


@editor_router.message(UserEditorState.waiting_for_key_name)
async def handle_key_name_input(message: types.Message, state: FSMContext):
    email = message.text.strip()
    key = await sync_to_async(Key.objects.filter(email=email).first)()

    if not key:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
        await message.answer("🔍 Ключ с указанным email не найден. 🚫", reply_markup=builder.as_markup())
        await state.clear()
        return

    user = await sync_to_async(lambda: key.user)()
    user_info, builder = await get_user_info(user, key)

    await message.answer(user_info, reply_markup=builder.as_markup())
    await state.set_state(UserEditorState.displaying_user_info)


@editor_router.message(UserEditorState.waiting_for_utm_source)
async def handle_utm_source_input(message: types.Message, state: FSMContext):
    utm_source = message.text.strip()
    users = await sync_to_async(list)(User.objects.filter(utm_source=utm_source))

    if not users:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
        await message.answer(f"🔍 Пользователи с UTM-меткой '{utm_source}' не найдены. 🚫", reply_markup=builder.as_markup())
        await state.clear()
        return

    user_count = len(users)
    response = f"🔗 Найдено пользователей с UTM-меткой '{utm_source}': {user_count}\n"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📥 Выгрузить рефералов в CSV", callback_data=f"export_utm_referrals_{utm_source}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))

    await message.answer(response, reply_markup=builder.as_markup())
    await state.clear()


async def generate_referrals_csv(data, filename_prefix, additional_info=None):
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    csv_data.write('\ufeff')

    header = [
        "│", "tg_id", "username", "first_name", "last_name",
        "language_code", "is_bot", "created_at_msk", "paid", "total_paid"
    ]

    async def write_recursive_referrals(cur_referrals, level=0, cur_prefix=[]):
        n = len(cur_referrals)
        for i, referral_or_user in enumerate(cur_referrals):
            if isinstance(referral_or_user, Referral):
                referred_user = referral_or_user.referred_user
            else:
                referred_user = referral_or_user
            created_at_msk = referred_user.created_at + timedelta(hours=3)
            total_paid = await sync_to_async(
                lambda: Payment.objects.filter(user=referred_user).aggregate(total=Sum('amount'))['total'] or 0
            )()
            paid = total_paid != 0
            is_last = i == n - 1
            cur_user = [
                '└─' if is_last else '├─',
                referred_user.tg_id,
                referred_user.username,
                referred_user.first_name,
                referred_user.last_name,
                referred_user.language_code,
                referred_user.is_bot,
                created_at_msk.strftime("%d.%m.%Y %H:%M:%S"),
                paid,
                total_paid,
            ]

            if i == 0:
                csv_writer.writerow(cur_prefix + ['│'])
                csv_writer.writerow(cur_prefix + header)
            csv_writer.writerow(cur_prefix + cur_user)

            referrals = await sync_to_async(list)(
                Referral.objects.filter(referrer_user=referred_user).select_related('referred_user')
            )
            if not referrals:
                continue
            await write_recursive_referrals(referrals, level + 1, cur_prefix + [' ' if is_last else '│'])

            if not is_last:
                csv_writer.writerow(cur_prefix + ['│'])

    if additional_info:
        for info in additional_info:
            csv_writer.writerow(info)

    await write_recursive_referrals(data)
    csv_data.seek(0)

    csv_content = csv_data.getvalue()
    csv_data.close()
    file = BufferedInputFile(csv_content.encode("utf-8-sig"), filename=f"{filename_prefix}.csv")
    return file


@editor_router.callback_query(F.data.startswith("export_referrals_"))
async def export_referrals_csv(callback_query: CallbackQuery, state: FSMContext):
    tg_id = int(callback_query.data.split("_")[-1])
    user = await sync_to_async(User.objects.filter(tg_id=tg_id).first)()
    try:
        await callback_query.message.delete()
    except Exception as e:
        pass

    if not user:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
        await callback_query.message.answer("🔍 Пользователь не найден. 🚫", reply_markup=builder.as_markup())
        await state.clear()
        await callback_query.answer()
        return

    referrals = await sync_to_async(list)(
        Referral.objects.filter(referrer_user=user).select_related('referred_user')
    )

    if not referrals:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
        await callback_query.message.answer("📭 У пользователя нет рефералов.", reply_markup=builder.as_markup())
        await state.clear()
        await callback_query.answer()
        return

    file = await generate_referrals_csv(referrals, f"referrals_{tg_id}")

    await callback_query.message.answer_document(
        file, caption=f"📥 Рефералы пользователя {user.username} (ID: {tg_id})"
    )
    await callback_query.answer()


@editor_router.callback_query(F.data.startswith("export_utm_referrals_"))
async def export_utm_referrals_csv(callback_query: CallbackQuery, state: FSMContext):
    utm_source = callback_query.data.split("_", 3)[-1]
    users = await sync_to_async(list)(User.objects.filter(utm_source=utm_source))
    try:
        await callback_query.message.delete()
    except Exception as e:
        pass

    if not users:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="user_editor"))
        await callback_query.message.answer(f"🔍 Пользователи с UTM-меткой '{utm_source}' не найдены. 🚫", reply_markup=builder.as_markup())
        await state.clear()
        await callback_query.answer()
        return

    file = await generate_referrals_csv(users, f"utm_referrals_{utm_source}")

    await callback_query.message.answer_document(
        file, caption=f"📥 Рефералы пользователей с UTM-меткой '{utm_source}'"
    )
    await callback_query.answer()

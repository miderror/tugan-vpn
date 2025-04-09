from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from django.conf import settings

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    
    text = "👋 Привет! Я бот для управления подпиской на VPN."
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Запустить", url=settings.WEBAPP_URL)
    )
    await message.answer(text, reply_markup=builder.as_markup())

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings

from handlers import start, admin

bot = Bot(
    token=settings.TELEGRAM_SECRET_KEY,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

dp.include_routers(
    admin.admin_router,
    start.router,
)
from aiogram import types
from aiogram.filters import BaseFilter
from django.conf import settings

class IsAdminFilter(BaseFilter):
    async def __call__(self, message: types.Message | types.CallbackQuery) -> bool:
        user_id = message.from_user.id
        print("User_id in admin_filter:", user_id)
        return user_id in settings.ADMIN_IDS

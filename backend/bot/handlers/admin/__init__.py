from aiogram import Router
from filters.admin_filter import IsAdminFilter
from .panel import panel_router
from .user_editor import editor_router

admin_router = Router()
admin_router.include_routers(
    panel_router,
    editor_router,
)

admin_router.message.filter(IsAdminFilter())
admin_router.callback_query.filter(IsAdminFilter())

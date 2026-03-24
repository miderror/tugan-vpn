import logging
from functools import wraps

from apps.core.models import User
from django.conf import settings
from telegram_webapp_auth import TelegramAuthenticator, generate_secret_key
from telegram_webapp_auth.errors import InvalidInitDataError

from .responses import R401, R405, R500

authenticator = TelegramAuthenticator(generate_secret_key(settings.BOT_TOKEN))
logger = logging.getLogger(__name__)


def twa_auth(method="GET"):
    def decorator(view_func):
        @wraps(view_func)
        async def _wrapped(request, *args, **kwargs):
            if request.method != method:
                return R405

            init_data_raw = request.headers.get("Telegram-Init-Data")
            if not init_data_raw:
                return R401

            try:
                init_data = authenticator.validate(init_data_raw)
            except InvalidInitDataError:
                return R401

            try:
                user = await User.objects.aget(telegram_id=init_data.user.id)
                request.user = user
            except User.DoesNotExist:
                request.user = await User.objects.acreate(
                    telegram_id=init_data.user.id,
                    first_name=init_data.user.first_name,
                    username=init_data.user.username,
                )

            try:
                return await view_func(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"API Error in {view_func.__name__}: {e}", exc_info=True)
                return R500

        return _wrapped

    return decorator

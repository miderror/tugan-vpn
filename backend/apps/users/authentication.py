import logging
from typing import Optional, Tuple

from django.conf import settings
from django.db import transaction
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from telegram_webapp_auth.auth import TelegramAuthenticator, generate_secret_key
from telegram_webapp_auth.errors import InvalidInitDataError

from apps.vpn.services import SubscriptionService

from .models import User
from .services import process_start_param

logger = logging.getLogger(__name__)


class TWAAuthentication(BaseAuthentication):
    def __init__(self):
        self.authenticator = TelegramAuthenticator(
            generate_secret_key(settings.TELEGRAM_BOT_TOKEN)
        )

    def authenticate(self, request: Request) -> Optional[Tuple[User, None]]:
        auth_header = request.headers.get("Telegram-Init-Data")

        if not auth_header:
            return None

        try:
            init_data = self.authenticator.validate(auth_header)
        except InvalidInitDataError as e:
            logger.warning(f"Invalid Telegram InitData received: {e}")
            raise AuthenticationFailed("Invalid Telegram authentication data")

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                telegram_id=init_data.user.id,
                defaults={
                    "username": init_data.user.username,
                    "first_name": init_data.user.first_name,
                    "last_name": init_data.user.last_name,
                    "language_code": init_data.user.language_code,
                },
            )

            if created:
                SubscriptionService.get_or_create_trial(user)
                logger.info(f"New user created: {user}")
                transaction.on_commit(
                    lambda: process_start_param(user, init_data.start_param)
                )

        return user, None

    def authenticate_header(self, request: Request) -> str:
        return "TWA"

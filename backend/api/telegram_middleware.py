import re
from django.conf import settings
from api.models import User, Connection, Referral
from rest_framework import status
from django.http import JsonResponse
from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import InvalidInitDataError
from telegram_webapp_auth.auth import generate_secret_key
from .services import xui
from bot.services.notification_service import send_referral_notification
from asgiref.sync import async_to_sync

class TWAAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        secret_key_bytes = generate_secret_key(settings.TELEGRAM_SECRET_KEY)
        self._telegram_authenticator = TelegramAuthenticator(secret_key_bytes)
        self.exact_paths = {
            '/api/ruleset/',
            '/api/tariffs/',
            '/api/yookassa/webhook/',
        }
        self.prefix_paths = (
            '/api/sub/',
            '/admin/',
        )

    def __call__(self, request):
        path = request.path
        if path in self.exact_paths or path.startswith(self.prefix_paths):
            return self.get_response(request)
        
        auth_cred = request.headers.get('Authorization')
        print(auth_cred)

        try:
            user = self._telegram_authenticator.verify_token(auth_cred)
        except InvalidInitDataError:
            return JsonResponse(data={"error": "Invalid Telegram init data"}, status=status.HTTP_401_UNAUTHORIZED)
        
        print("user:", user)
        current_user = User.objects.filter(tg_id=user.id).first()
        if not current_user:
            current_user = User.objects.create(
                tg_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code,
                is_bot=False
            )

            connection = Connection.objects.create(tg_id=current_user)
            request.connection = connection
            
            async_to_sync(xui.create_client)(
                current_user.tg_id, days=7, total_bytes=int(settings.TOTAL_GB * 1024 * 1024 * 1024), is_active=True
            )

            print("создан клиент")
            start_param = self._get_start_param(request)
            print("проверка start_param")
            if start_param:
                start_param = str(start_param)
                if start_param.isdigit():
                    referrer_id = int(start_param)
                    if current_user.tg_id != referrer_id:
                        try:
                            referrer_user = User.objects.get(tg_id=referrer_id)
                            Referral.objects.create(
                                referred_user=current_user,
                                referrer_user=referrer_user,
                                reward_issued=False
                            )
                            async_to_sync(xui.extend_access)(
                                referrer_id, days=14, total_bytes=int(settings.TOTAL_GB * 1024 * 1024 * 1024)
                            )
                            async_to_sync(send_referral_notification)(referrer_id, current_user.username)
                            print("Set referrer:", referrer_id)
                        except Exception as e:
                            print(f"Error creating referral: {e}")
                elif self._is_valid_utm(start_param):
                        current_user.utm_source = start_param
                        current_user.save()
        else:
            request.connection = Connection.objects.filter(tg_id=current_user).first()

        request.tg_user = current_user
        print(f"Request user set to: {request.tg_user}")
        print(f"Request connection set to: {request.connection}")

        response = self.get_response(request)

        return response

    def _get_start_param(self, request):
        try:
            return request.GET.get('start_param')
        except Exception as e:
            print("ошибка получения start_param:", e)
            return None

    def _is_valid_utm(self, value):
        return (
            len(value) <= 64 and 
            re.match(r'^[a-zA-Z0-9_]+$', value) is not None
        )
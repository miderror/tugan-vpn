import json
from django.conf import settings
from api.models import User, Connection, Referral
from rest_framework import status
from django.http import JsonResponse
from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import InvalidInitDataError
from telegram_webapp_auth.auth import generate_secret_key

class TWAAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        secret_key_bytes = generate_secret_key(settings.TELEGRAM_SECRET_KEY)
        self._telegram_authenticator = TelegramAuthenticator(secret_key_bytes)

    def __call__(self, request):
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
            
            referrer_id = self._get_referrer_id(request)
            if referrer_id and current_user.tg_id != referrer_id:
                try:
                    referrer_user = User.objects.get(tg_id=referrer_id)
                    Referral.objects.create(
                        referred_tg_id=current_user,
                        referrer_tg_id=referrer_user,
                        reward_issued=False
                    )
                    print("Set referrer:", referrer_id)
                except Exception as e:
                    print(f"Error creating referral: {e}")
        else:
            request.connection = Connection.objects.filter(tg_id=current_user).first()

        request.tg_user = current_user
        print(f"Request user set to: {request.tg_user}")
        print(f"Request connection set to: {request.connection}")

        response = self.get_response(request)

        return response

    def _get_referrer_id(self, request):
        data = json.loads(request.body)
        referrer_id = data.get('referrer_id')
        if referrer_id:
            try:
                return int(referrer_id)
            except (ValueError, TypeError):
                return None
        return None
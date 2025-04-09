import requests
from django.conf import settings
from django.http import HttpResponse, Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, Referral, Tariff
from .serializers import (
    UserSerializer,
    ReferralSerializer,
    TariffSerializer
)


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        print(request)
        print(request.tg_user)
        print(request.user.is_authenticated)
        user = request.tg_user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def avatar(self, request, pk=None):
        user = self.get_object(pk)
        print(user.tg_id)
        bot_token = settings.TELEGRAM_SECRET_KEY
        try:
            photos_response = requests.get(
                f'https://api.telegram.org/bot{bot_token}/getUserProfilePhotos?user_id={user.tg_id}'
            )
            photos_response.raise_for_status()

            photos = photos_response.json()['result']['photos']

            if not photos or len(photos) == 0:
                raise ValueError('Not found')

            file_id = photos[0][0]['file_id']

            file_response = requests.get(
                f'https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}'
            )
            file_response.raise_for_status()

            file_path = file_response.json()['result']['file_path']

            photo_url = f'https://api.telegram.org/file/bot{bot_token}/{file_path}'
            photo_response = requests.get(photo_url)
            photo_response.raise_for_status()

            response = HttpResponse(photo_response.content, content_type='image/jpeg')
            response['Cache-Control'] = 'public, max-age=86400'
            return response
        except Exception as e:
            response = HttpResponse(status=404)
            response['Cache-Control'] = 'public, max-age=86400'
            return response


class ReferralViewSet(viewsets.ViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer

    @action(detail=False, methods=['get'])
    def get_referrals(self, request):
        current_user = request.tg_user
        referrals = Referral.objects.filter(referrer_user=current_user)

        referral_data = []
        for referral in referrals:
            referred_user = referral.referred_user
            referral_data.append({
                'id': referred_user.tg_id,
                'username': referred_user.username,
            })

        return Response(referral_data, status=status.HTTP_200_OK)


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
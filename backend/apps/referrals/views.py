from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.models import User

from .serializers import ReferralUserSerializer


class ReferralViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralUserSerializer

    def get_queryset(self):
        return User.objects.filter(referred_by=self.request.user).only(
            "telegram_id", "username"
        )

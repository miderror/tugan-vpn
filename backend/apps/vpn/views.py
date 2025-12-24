from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.serializers import UserProfileSerializer

from .models import Subscription, Tariff
from .serializers import TariffSerializer


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tariff.objects.filter(is_active=True).order_by("order")
    serializer_class = TariffSerializer
    permission_classes = [IsAuthenticated]


class VpnViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def config(self, request):
        try:
            sub = request.user.subscription
            if not sub.is_active:
                return Response({"vpn_url": ""})
            return Response({"vpn_url": sub.vless_link})
        except Subscription.DoesNotExist:
            return Response({"vpn_url": ""})

    @action(detail=False, methods=["post"])
    def claim_gift(self, request):
        user = request.user
        if not hasattr(user, "subscription"):
            return Response(
                {"detail": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND
            )

        sub = user.subscription
        if sub.trial_activated:
            return Response(
                {"detail": "Gift already claimed"}, status=status.HTTP_400_BAD_REQUEST
            )

        sub.trial_activated = True
        sub.save(update_fields=["trial_activated"])

        return Response(UserProfileSerializer(user, context={"request": request}).data)

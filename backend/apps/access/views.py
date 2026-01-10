import base64

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.serializers import UserProfileSerializer

from .models import Subscription, Tariff, VpnServer
from .serializers import TariffSerializer


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tariff.objects.filter(is_active=True)
    serializer_class = TariffSerializer
    permission_classes = [IsAuthenticated]


class VpnViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="claim-gift")
    def claim_gift(self, request):
        user = request.user
        if not hasattr(user, "subscription"):
            return Response(
                {"detail": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND
            )

        sub = user.subscription
        if sub.trial_activated:
            return Response(
                {"detail": "Gift already claimed"}, status=status.HTTP_409_CONFLICT
            )

        sub.trial_activated = True
        sub.save(update_fields=["trial_activated"])

        return Response(UserProfileSerializer(user, context={"request": request}).data)


class SubscriptionFileView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        sub = get_object_or_404(Subscription, access_token=token)

        if not sub.has_ever_connected:
            sub.has_ever_connected = True
            sub.save(update_fields=["has_ever_connected"])

        active_servers = VpnServer.objects.filter(is_active=True).only(
            "config_template"
        )
        configs = []

        for server in active_servers:
            try:
                configs.append(server.config_template.format(uuid=str(sub.vless_uuid)))
            except Exception:
                continue

        if not configs:
            return HttpResponseBadRequest("No active servers")

        combined_config = "\n".join(configs)
        base64_encoded = base64.b64encode(combined_config.encode("utf-8")).decode(
            "utf-8"
        )

        expiry_time = int(sub.end_date.timestamp())

        profile_title = settings.APP_PROFILE_TITLE
        title_b64 = base64.b64encode(profile_title.encode("utf-8")).decode("utf-8")

        response = HttpResponse(
            base64_encoded, content_type="text/plain; charset=utf-8"
        )
        response["Content-Disposition"] = "inline"
        response["profile-update-interval"] = "12"
        response["profile-title"] = f"base64:{title_b64}"
        response["subscription-userinfo"] = (
            f"upload=0; download={sub.used_bytes}; "
            f"total={sub.total_bytes_limit}; expire={expiry_time}"
        )
        return response

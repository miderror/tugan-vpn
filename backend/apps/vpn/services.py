import asyncio
import logging
from datetime import timedelta

from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from infrastructure.vpn.client import VpnClientDTO, VpnError, XuiAdapter, XuiCredentials

from apps.users.models import User

from .models import Subscription, Tariff, VpnServer

logger = logging.getLogger("apps.vpn")


class SubscriptionService:
    @staticmethod
    def get_or_create_trial(user: User) -> Subscription:
        if hasattr(user, "subscription"):
            return user.subscription

        end_date = timezone.now() + timedelta(days=7)
        return Subscription.objects.create(user=user, end_date=end_date)

    @staticmethod
    def extend_subscription(user: User, tariff: Tariff) -> Subscription:
        sub, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                "end_date": timezone.now() + timedelta(days=tariff.duration_days)
            },
        )

        if not created:
            start_point = max(timezone.now(), sub.end_date)
            sub.end_date = start_point + timedelta(days=tariff.duration_days)
            sub.save(update_fields=["end_date"])

        return sub


class VpnServerService:
    def _get_credentials(self, server: VpnServer) -> XuiCredentials:
        return XuiCredentials(
            url=server.api_url,
            username=server.api_username,
            password=server.api_password,
        )

    def _prepare_dto(self, sub: Subscription) -> VpnClientDTO:
        return VpnClientDTO(
            email=sub.email,
            uuid=str(sub.vless_uuid),
            enable=sub.is_active,
            total_gb=sub.total_bytes_limit,
            expiry_time=int(sub.end_date.timestamp() * 1000),
            sub_id=sub.sub_id,
            flow=settings.XUI_CLIENT_FLOW,
            limit_ip=settings.XUI_CLIENT_LIMIT_IP,
        )

    async def sync_subscription(self, sub: Subscription):
        active_servers = await sync_to_async(list)(
            VpnServer.objects.filter(is_active=True)
        )

        if not active_servers:
            logger.warning(f"No active servers for user {sub.user_id}")
            return

        dto = self._prepare_dto(sub)

        async def _sync_one(server: VpnServer):
            creds = self._get_credentials(server)
            adapter = XuiAdapter(creds)
            try:
                async with adapter:
                    await adapter.upsert_client(server.inbound_id, dto)
            except VpnError:
                pass

        await asyncio.gather(*(_sync_one(s) for s in active_servers))

    async def update_traffic_usage(self, sub: Subscription) -> int:
        active_servers = await sync_to_async(list)(
            VpnServer.objects.filter(is_active=True)
        )

        async def _get_one(server: VpnServer) -> int:
            creds = self._get_credentials(server)
            adapter = XuiAdapter(creds)
            try:
                async with adapter:
                    return await adapter.get_traffic(sub.email)
            except VpnError:
                return 0

        results = await asyncio.gather(*(_get_one(s) for s in active_servers))
        total = sum(results)

        if total > 0:
            sub.used_bytes = total
            sub.last_traffic_update = timezone.now()
            await sub.asave(update_fields=["used_bytes", "last_traffic_update"])

        return total

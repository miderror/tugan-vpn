import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from django.conf import settings
from django.core.cache import cache
from django.db.models import BooleanField, Case, Value, When
from django.utils import timezone
from infrastructure.vpn.adapter import XuiAdapter

from apps.access.models import Subscription, VpnServer

logger = logging.getLogger(__name__)

BULK_THRESHOLD = 20


class SyncService:
    def __init__(self):
        self.flow = getattr(settings, "XUI_CLIENT_FLOW", "xtls-rprx-vision")
        self.limit_ip = getattr(settings, "XUI_CLIENT_LIMIT_IP", 1)

    @asynccontextmanager
    async def _server_lock(self, server_id: int):
        key = f"vpn_lock:srv:{server_id}"
        acquired = False
        try:
            for _ in range(20):
                if cache.add(key, "1", timeout=60):
                    acquired = True
                    break
                await asyncio.sleep(0.1)

            if not acquired:
                raise TimeoutError(f"Server {server_id} busy")

            yield
        finally:
            if acquired:
                cache.delete(key)

    def _get_payload(self, target_ids: Optional[List[int]] = None) -> List[Dict]:
        now = timezone.now()
        qs = Subscription.objects.all()

        if target_ids is not None:
            qs = qs.filter(user__telegram_id__in=target_ids)

        data = qs.annotate(
            should_enable=Case(
                When(is_vpn_client_active=True, end_date__gt=now, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).values("vless_uuid", "email", "sub_id", "should_enable", "end_date")

        return [
            {
                "id": str(row["vless_uuid"]),
                "email": row["email"],
                "enable": row["should_enable"],
                "totalGB": 0,
                "expiryTime": int(row["end_date"].timestamp() * 1000),
                "subId": row["sub_id"],
                "flow": self.flow,
                "limitIp": self.limit_ip,
            }
            for row in data
        ]

    async def _sync_one_server(self, server: Dict, user_ids: Optional[List[int]]):
        s_id = server["id"]
        inbound_id = server["inbound_id"]
        creds = server["credentials"]

        is_partial = (user_ids is not None) and (len(user_ids) < BULK_THRESHOLD)
        ids_to_fetch = user_ids if is_partial else None

        payload = self._get_payload(ids_to_fetch)
        if not payload and not is_partial:
            return

        try:
            async with self._server_lock(s_id):
                adapter = XuiAdapter(
                    creds["api_url"], creds["username"], creds["password"]
                )
                async with adapter:
                    if is_partial:
                        tasks = [adapter.update_client(inbound_id, p) for p in payload]
                        await asyncio.gather(*tasks, return_exceptions=True)
                    else:
                        await adapter.bulk_overwrite(inbound_id, payload)
        except Exception as e:
            logger.error(f"Sync error srv={s_id}: {e}")

    async def sync_all(self, user_ids: Optional[List[int]] = None):
        servers = list(
            VpnServer.objects.filter(is_active=True).values(
                "id", "inbound_id", "credentials"
            )
        )

        tasks = [self._sync_one_server(srv, user_ids) for srv in servers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def collect_traffic(self) -> Dict[str, int]:
        servers = list(
            VpnServer.objects.filter(is_active=True).values(
                "id", "inbound_id", "credentials"
            )
        )
        total_usage = {}

        async def _worker(srv):
            try:
                async with self._server_lock(srv["id"]):
                    creds = srv["credentials"]
                    adapter = XuiAdapter(
                        creds["api_url"], creds["username"], creds["password"]
                    )
                    async with adapter:
                        return await adapter.get_traffic_and_reset(srv["inbound_id"])
            except Exception as e:
                logger.error(f"Traffic error srv={srv['id']}: {e}")
                return {}

        results = await asyncio.gather(*[_worker(s) for s in servers])

        for res in results:
            if not res:
                continue
            for email, val in res.items():
                total_usage[email] = total_usage.get(email, 0) + val

        return total_usage

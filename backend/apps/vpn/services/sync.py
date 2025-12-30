import asyncio
import logging
from typing import List

from django.conf import settings
from infrastructure.vpn.adapter import XuiAdapter
from infrastructure.vpn.dtos import VpnClientConfig, XuiCredentials

from .dtos import ServerConnDTO, UserSyncDTO
from .selector import VpnSelector

logger = logging.getLogger(__name__)


class VpnSyncService:
    def __init__(self):
        self.flow = settings.XUI_CLIENT_FLOW
        self.limit_ip = settings.XUI_CLIENT_LIMIT_IP

    def _to_adapter_config(self, user: UserSyncDTO) -> VpnClientConfig:
        return VpnClientConfig(
            vless_uuid=user.vless_uuid,
            email=user.email,
            enable=user.is_enable,
            total_bytes=user.total_gb,
            expiry_time_ms=user.expiry_time_ms,
            sub_id=user.sub_id,
            flow=self.flow,
            limit_ip=self.limit_ip,
        )

    async def _push_single_user(self, server: ServerConnDTO, config: VpnClientConfig):
        creds = XuiCredentials(
            url=server.api_url, username=server.username, password=server.password
        )
        adapter = XuiAdapter(creds)
        async with adapter:
            await adapter.upsert_client(server.inbound_id, config)

    async def _push_bulk_users(
        self, server: ServerConnDTO, configs: List[VpnClientConfig]
    ):
        creds = XuiCredentials(
            url=server.api_url, username=server.username, password=server.password
        )
        adapter = XuiAdapter(creds)
        async with adapter:
            await adapter.bulk_overwrite_clients(server.inbound_id, configs)

    async def sync_user_to_server(self, sub_id: int, server_id: int):
        user = VpnSelector.get_user(sub_id)
        server = VpnSelector.get_server(server_id)

        config = self._to_adapter_config(user)

        await self._push_single_user(server, config)

    async def sync_user_everywhere(self, sub_id: int):
        user = VpnSelector.get_user(sub_id)
        servers = VpnSelector.get_all_active_servers()

        config = self._to_adapter_config(user)

        tasks = [self._push_single_user(server, config) for server in servers]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for srv, res in zip(servers, results):
            if isinstance(res, Exception):
                logger.error(
                    f"Sync failed for user {user.email} on {srv.api_url}: {res}"
                )

    async def sync_server_full(self, server_id: int):
        server = VpnSelector.get_server(server_id)
        users = VpnSelector.get_all_users()

        configs = [self._to_adapter_config(u) for u in users]

        await self._push_bulk_users(server, configs)

    async def sync_all_servers_full(self):
        users = VpnSelector.get_all_users()
        servers = VpnSelector.get_all_active_servers()

        configs = [self._to_adapter_config(u) for u in users]

        tasks = [self._push_bulk_users(server, configs) for server in servers]

        await asyncio.gather(*tasks, return_exceptions=True)

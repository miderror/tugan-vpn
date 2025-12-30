import logging
from typing import Dict, List, Optional

from py3xui import AsyncApi
from py3xui import Client as XuiClientObj

from .dtos import VpnClientConfig, XuiCredentials

logger = logging.getLogger(__name__)


class VpnAdapterError(Exception):
    pass


class AuthenticationError(VpnAdapterError):
    pass


class XuiAdapter:
    def __init__(self, credentials: XuiCredentials):
        self._creds = credentials
        self._api: Optional[AsyncApi] = None

    async def __aenter__(self):
        try:
            self._api = AsyncApi(
                self._creds.url, self._creds.username, self._creds.password
            )
            await self._api.login()
            return self
        except Exception as e:
            logger.error(f"XUI Login failed for {self._creds.url}: {e}")
            raise AuthenticationError(f"Login failed: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def _to_xui_client(self, config: VpnClientConfig) -> XuiClientObj:
        return XuiClientObj(
            id=str(config.vless_uuid),
            email=config.email,
            enable=config.enable,
            totalGB=config.total_bytes,
            expiryTime=config.expiry_time_ms,
            subId=config.sub_id,
            flow=config.flow,
            limitIp=config.limit_ip,
        )

    async def upsert_client(self, inbound_id: int, config: VpnClientConfig) -> None:
        if not self._api:
            raise VpnAdapterError("Session not initialized")

        try:
            xui_client = self._to_xui_client(config)
            existing = await self._api.client.get_by_email(config.email)

            if existing:
                await self._api.client.update(existing.id, xui_client)
                logger.debug(f"Updated client {config.email} on inbound {inbound_id}")
            else:
                await self._api.client.add(inbound_id, [xui_client])
                logger.debug(f"Added client {config.email} to inbound {inbound_id}")

        except Exception as e:
            logger.error(f"Upsert failed for {config.email}: {e}")
            raise VpnAdapterError(f"Upsert error: {e}")

    async def bulk_overwrite_clients(
        self, inbound_id: int, configs: List[VpnClientConfig]
    ) -> None:
        if not self._api:
            raise VpnAdapterError("Session not initialized")

        try:
            inbound = await self._api.inbound.get_by_id(inbound_id)
            if not inbound or not inbound.settings:
                raise VpnAdapterError(f"Inbound {inbound_id} not found or invalid")

            new_clients = [self._to_xui_client(c) for c in configs]

            inbound.settings.clients = new_clients
            await self._api.inbound.update(inbound_id, inbound)
            logger.info(
                f"Bulk synced {len(new_clients)} clients to inbound {inbound_id}"
            )

        except Exception as e:
            logger.error(f"Bulk sync failed for inbound {inbound_id}: {e}")
            raise VpnAdapterError(f"Bulk sync failed: {e}")

    async def get_inbound_stats(self, inbound_id: int) -> Dict[str, int]:
        if not self._api:
            raise VpnAdapterError("Session not initialized")

        try:
            inbound = await self._api.inbound.get_by_id(inbound_id)
            stats = {}

            if inbound and inbound.clientStats:
                for stat in inbound.clientStats:
                    stats[stat.email] = stat.up + stat.down

            logger.debug(
                f"Retrieved traffic stats for {len(stats)} users on inbound {inbound_id}"
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats for inbound {inbound_id}: {e}")
            raise VpnAdapterError(f"Stats error: {e}")

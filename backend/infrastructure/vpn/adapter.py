import logging
from typing import Any, Dict, List, Optional

from py3xui import AsyncApi
from py3xui import Client as XuiClientObj

logger = logging.getLogger(__name__)


class XuiAdapter:
    __slots__ = ("_url", "_username", "_password", "_api")

    def __init__(self, url: str, username: str, password: str):
        self._url = url
        self._username = username
        self._password = password
        self._api: Optional[AsyncApi] = None

    async def __aenter__(self):
        self._api = AsyncApi(self._url, self._username, self._password)
        try:
            await self._api.login()
        except Exception as e:
            logger.error(f"XUI Login failed: {self._url} - {e}")
            raise ConnectionError(f"VPN Login failed: {e}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def update_client(self, inbound_id: int, client_data: Dict[str, Any]) -> None:
        if not self._api:
            raise ConnectionError("Session not initialized")

        client = XuiClientObj(inboundId=inbound_id, **client_data)

        try:
            try:
                await self._api.client.update(client.id, client)
            except Exception:
                await self._api.client.add(client.id, [client])
        except Exception as e:
            logger.error(
                f"Failed to upsert client {client.email} on inbound {inbound_id}: {e}"
            )
            raise

    async def bulk_overwrite(
        self, inbound_id: int, clients_data: List[Dict[str, Any]]
    ) -> None:
        if not self._api:
            raise ConnectionError("Session not initialized")

        try:
            inbound = await self._api.inbound.get_by_id(inbound_id)
            inbound.settings.clients = [
                XuiClientObj(inboundId=inbound_id, **c) for c in clients_data
            ]

            await self._api.inbound.update(inbound_id, inbound)
        except Exception as e:
            logger.error(f"Bulk overwrite failed on inbound {inbound_id}: {e}")
            raise

    async def get_traffic_and_reset(self, inbound_id: int) -> Dict[str, int]:
        if not self._api:
            raise ConnectionError("Session not initialized")

        try:
            inbound = await self._api.inbound.get_by_id(inbound_id)
            stats = {}
            if inbound and inbound.clientStats:
                stats = {
                    s.email: (s.up + s.down)
                    for s in inbound.clientStats
                    if (s.up + s.down) > 0
                }

            if stats:
                await self._api.inbound.reset_client_stats(inbound_id)

            return stats
        except Exception as e:
            logger.error(f"Traffic sync failed: {e}")
            return {}

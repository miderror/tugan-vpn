import logging
from dataclasses import dataclass
from typing import Optional

from py3xui import AsyncApi
from py3xui import Client as XuiClientObj

logger = logging.getLogger("infrastructure.vpn")


@dataclass
class XuiCredentials:
    url: str
    username: str
    password: str


@dataclass
class VpnClientDTO:
    email: str
    uuid: str
    enable: bool
    total_gb: int
    expiry_time: int
    sub_id: str
    flow: str
    limit_ip: int


class VpnError(Exception):
    pass


class XuiAdapter:
    def __init__(self, creds: XuiCredentials):
        self.creds = creds
        self.api: Optional[AsyncApi] = None

    async def __aenter__(self):
        try:
            self.api = AsyncApi(
                host=self.creds.url,
                username=self.creds.username,
                password=self.creds.password,
            )
            await self.api.login()
            return self
        except Exception as e:
            logger.error(f"XUI Login failed ({self.creds.url}): {e}")
            raise VpnError(f"Connection error: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def upsert_client(self, inbound_id: int, client: VpnClientDTO) -> None:
        if not self.api:
            raise VpnError("Context not started")

        try:
            xui_client = XuiClientObj(
                id=client.uuid,
                email=client.email,
                enable=client.enable,
                totalGB=client.total_gb,
                expiryTime=client.expiry_time,
                subId=client.sub_id,
                flow=client.flow,
                limitIp=client.limit_ip,
            )

            existing = await self.api.client.get_by_email(client.email)

            if existing:
                await self.api.client.update(client.uuid, xui_client)
                logger.info(f"Updated client {client.email}")
            else:
                await self.api.client.add(inbound_id, [xui_client])
                logger.info(f"Created client {client.email}")

        except Exception as e:
            logger.error(f"Upsert failed for {client.email}: {e}")
            raise VpnError(f"Upsert error: {e}")

    async def get_traffic(self, email: str) -> int:
        if not self.api:
            raise VpnError("Context not started")
        try:
            c = await self.api.client.get_by_email(email)
            return (c.up + c.down) if c else 0
        except Exception:
            return 0

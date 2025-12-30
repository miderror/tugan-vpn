from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel, Field


@dataclass
class XuiCredentials:
    url: str
    username: str
    password: str


class VpnClientConfig(BaseModel):
    vless_uuid: UUID
    email: str
    enable: bool
    total_bytes: int = Field(ge=0)
    expiry_time_ms: int = Field(ge=0)
    sub_id: str
    flow: str = "xtls-rprx-vision"
    limit_ip: int = 1

    class Config:
        frozen = True

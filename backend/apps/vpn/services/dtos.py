from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ServerConnDTO(BaseModel):
    id: int
    api_url: str
    username: str
    password: str
    inbound_id: int

    model_config = ConfigDict(frozen=True)


class UserSyncDTO(BaseModel):
    telegram_id: int
    vless_uuid: UUID
    email: str
    is_enable: bool
    total_gb: int
    expiry_time_ms: int
    sub_id: str

    model_config = ConfigDict(frozen=True)

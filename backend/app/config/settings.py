import base64
from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    debug: bool = Field(default=False, alias="DEBUG")

    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    redis_host: str = Field(default="redis", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str | None = Field(default=None, alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    admin_path_raw: str = Field(default="admin", alias="ADMIN_PATH")
    admin_ids_raw: str = Field(default="", alias="ADMIN_IDS")

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(alias="TELEGRAM_WEBHOOK_SECRET")
    telegram_webhook_url : str = Field(alias="TELEGRAM_WEBHOOK_URL")

    default_traffic_limit_bytes: int = Field(
        default=268_435_456_000, alias="DEFAULT_TRAFFIC_LIMIT_BYTES"
    )

    yookassa_shop_id: str = Field(alias="YOOKASSA_SHOP_ID")
    yookassa_secret_key: str = Field(alias="YOOKASSA_SECRET_KEY")
    webapp_url: str = Field(alias="WEBAPP_URL")

    @property
    def admin_path(self) -> str:
        clean_path = self.admin_path_raw.strip("/")
        return f"/{clean_path}"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @cached_property
    def yookassa_auth_header(self) -> str:
        credentials = f"{self.yookassa_shop_id}:{self.yookassa_secret_key}".encode()
        return f"Basic {base64.b64encode(credentials).decode()}"

    @cached_property
    def admin_ids(self) -> list[int]:
        if not self.admin_ids_raw:
            return []
        return [
            int(x.strip()) for x in self.admin_ids_raw.split(",") if x.strip().isdigit()
        ]


settings = AppSettings()

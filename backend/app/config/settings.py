from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

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

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")

    default_traffic_limit_bytes: int = Field(
        default=268_435_456_000, alias="DEFAULT_TRAFFIC_LIMIT_BYTES"
    )

    @property
    def admin_path(self) -> str:
        clean_path = self.admin_path_raw.strip("/")
        return f"/{clean_path}"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = AppSettings()

from pathlib import Path

from pydantic import BaseModel, HttpUrl, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from shopucdyadya.app.openapi import OpenAPIConfig

BASE_DIR = Path(__file__).parent.parent.parent.parent


class AppConfig(BaseModel):
    allow_credentials: bool = False
    allow_methods: list[str] = ["GET", "POST", "PATCH"]
    allow_headers: list[str] = ["Content-Type", "X-Telegram-Init-Data"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: AppConfig = AppConfig()
    openapi: OpenAPIConfig = OpenAPIConfig()
    cors_origins: list[str] = []
    runtime_db_url: PostgresDsn | None = None
    migration_db_url: PostgresDsn | None = None
    proxy_url: SecretStr | None = None
    bot_token: SecretStr | None = None
    webapp_url: HttpUrl | None = None

    def require_runtime_db_url(self) -> PostgresDsn:
        if self.runtime_db_url is None:
            raise ValueError("RUNTIME_DB_URL must be configured for this process")
        return self.runtime_db_url

    def require_migration_db_url(self) -> PostgresDsn:
        if self.migration_db_url is None:
            raise ValueError("MIGRATION_DB_URL must be configured for db-init")
        return self.migration_db_url


settings = Settings()

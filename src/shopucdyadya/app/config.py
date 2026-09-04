from pathlib import Path

from pydantic import AmqpDsn, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from shopucdyadya.app.factory import AppConfig
from shopucdyadya.app.openapi import OpenAPIConfig

BASE_DIR = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: AppConfig = AppConfig()
    openapi: OpenAPIConfig = OpenAPIConfig()
    cache_url: RedisDsn
    db_url: PostgresDsn
    broker_url: AmqpDsn


settings = Settings()

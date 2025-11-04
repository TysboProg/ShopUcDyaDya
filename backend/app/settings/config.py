from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class RunConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000


class GunicornConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2
    timeout: int = 900


class LoggingSettings(BaseSettings):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT


class DatabaseSettings(BaseSettings):
    user: str
    password: str
    name: str
    port: int = Field(default=5432, alias="PORT")

    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_prefix="DB_")

    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn(
            url=f"postgresql+asyncpg://{self.user}:{self.password}@pg:{self.port}/{self.name}",
        )


class RedisSettings(BaseSettings):
    port: int = Field(default=6379, alias="PORT")

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_prefix="REDIS_",
    )

    @property
    def url(self) -> RedisDsn:
        return RedisDsn(
            url=f"redis://redis:{self.port}/0",
        )


class Settings(BaseSettings):
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    run: RunConfig = Field(default_factory=RunConfig)
    gunicorn: GunicornConfig = Field(default_factory=GunicornConfig)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
    )


settings = Settings()
print(settings.db.url.encoded_string())

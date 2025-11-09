from typing import Literal

from pydantic import AmqpDsn, Field, PostgresDsn, RedisDsn
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

    @property
    def url_sync(self) -> PostgresDsn:
        return PostgresDsn(
            url=f"postgresql+psycopg2://{self.user}:{self.password}@pg:{self.port}/{self.name}",
        )


class RabbitSettings(BaseSettings):
    port: int = Field(default=5672, alias="PORT")
    username: str = Field(default="guest", alias="USERNAME")
    password: str = Field(default="guest", alias="PASSWORD")

    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_prefix="RABBIT_")

    @property
    def url(self) -> AmqpDsn:
        return AmqpDsn(url=f"amqp://{self.username}:{self.password}@rabbitmq:{self.port}//")


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
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)
    run: RunConfig = Field(default_factory=RunConfig)
    gunicorn: GunicornConfig = Field(default_factory=GunicornConfig)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
    )


settings = Settings()

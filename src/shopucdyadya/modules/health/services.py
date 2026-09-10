import logging

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from taskiq_aio_pika import AioPikaBroker

logger = logging.getLogger(__name__)


class DatabaseHealthCheck:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def is_available(self) -> bool:
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except Exception:
            logger.warning("Database is unavailable")
            return False
        return True


class RedisHealthCheck:
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def is_available(self) -> bool:
        try:
            return bool(await self._client.ping())
        except Exception:
            logger.warning("Redis is unavailable")
            return False


class BrokerHealthCheck:
    def __init__(self, broker: AioPikaBroker) -> None:
        self._broker = broker

    async def is_available(self) -> bool:
        try:
            if self._broker.write_conn is None or self._broker.write_conn.is_closed:
                await self._broker.startup()
        except Exception:
            logger.warning("Broker is unavailable")
            return False

        return self._broker.write_conn is not None and not self._broker.write_conn.is_closed

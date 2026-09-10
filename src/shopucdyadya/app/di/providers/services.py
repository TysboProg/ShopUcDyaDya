from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from taskiq_aio_pika import AioPikaBroker

from shopucdyadya.modules.health.services import (
    BrokerHealthCheck,
    DatabaseHealthCheck,
    RedisHealthCheck,
)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_database_health_check(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> DatabaseHealthCheck:
        return DatabaseHealthCheck(session_factory)

    @provide
    def get_redis_health_check(self, client: Redis) -> RedisHealthCheck:
        return RedisHealthCheck(client)

    @provide
    def get_broker_health_check(self, broker: AioPikaBroker) -> BrokerHealthCheck:
        return BrokerHealthCheck(broker)

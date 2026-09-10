from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from shopucdyadya.app.config import settings


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis_client(self) -> AsyncGenerator[Redis]:
        client = Redis.from_url(settings.cache_url.encoded_string(), decode_responses=True)
        yield client
        await client.aclose()

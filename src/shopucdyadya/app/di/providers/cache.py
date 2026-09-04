from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from shopucdyadya.app.config import settings


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncIterable[Redis]:
        # Открываем соединение при старте приложения
        client = Redis.from_url(settings.cache_url.encoded_string())
        yield client
        # Закрываем соединение при остановке приложения
        await client.aclose()

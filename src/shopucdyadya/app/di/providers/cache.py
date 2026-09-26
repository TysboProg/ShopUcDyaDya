from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine

from shopucdyadya.app.cache import AiogramCache, PgCache


class CacheProvider(Provider):
    """Ядро — доступно и FastAPI, и aiogram."""

    @provide(scope=Scope.APP)
    def get_pg_cache(self, engine: AsyncEngine) -> PgCache:
        return PgCache(engine)

    @provide(scope=Scope.APP)
    def get_aiogram_cache(self, core: PgCache) -> AiogramCache:
        return AiogramCache(core)

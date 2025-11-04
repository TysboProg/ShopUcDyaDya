from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DatabaseProvider(Provider):
    """Провайдер для зависимостей базы данных"""

    def __init__(self, url: str):
        self.url = url
        super().__init__()

    @provide(scope=Scope.APP)
    def create_engine(self) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            url=self.url,
            pool_pre_ping=True,
        )

        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
        )

        return session_factory

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

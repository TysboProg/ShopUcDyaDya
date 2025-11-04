from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from settings.config import settings


class DatabaseProvider(Provider):
    """Провайдер для зависимостей базы данных"""
    @provide(scope=Scope.APP)
    def create_engine(self) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            settings.db.url.encoded_string(),
            pool_pre_ping=True,
        )

        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
        )

        return session_factory

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
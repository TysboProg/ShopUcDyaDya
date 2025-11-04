from collections.abc import AsyncGenerator
import pytest_asyncio
from dishka import Provider, provide, Scope, make_async_container
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from application.di.providers import (
    ServiceProvider,
    RepositoryProvider,
    PromoValidatorProvider
)


class TestDatabaseProvider(Provider):
    """Тестовый провайдер для базы данных"""

    @provide(scope=Scope.APP)
    def create_engine(self) -> async_sessionmaker[AsyncSession]:
        test_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        test_session_factory = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        return test_session_factory

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


@pytest_asyncio.fixture
async def dishka_container():
    """Создает тестовый контейнер Dishka"""
    container = make_async_container(
        TestDatabaseProvider(),
        ServiceProvider(),
        RepositoryProvider(),
        PromoValidatorProvider(),
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def db_session(dishka_container) -> AsyncGenerator[AsyncSession]:
    """Фикстура для тестовой сессии"""
    async with dishka_container() as request_container:
        session = await request_container.get(AsyncSession)
        yield session
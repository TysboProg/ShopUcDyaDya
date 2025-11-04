from collections.abc import AsyncGenerator

import pytest_asyncio
from application.di.providers import (
    DatabaseProvider,
    PromoValidatorProvider,
    RepositoryProvider,
    ServiceProvider,
)
from dishka import make_async_container
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def dishka_container():
    """Создает тестовый контейнер Dishka"""
    container = make_async_container(
        DatabaseProvider(url="sqlite+aiosqlite:///:memory:"),
        ServiceProvider(),
        RepositoryProvider(),
        PromoValidatorProvider(),
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def db_session(dishka_container) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для тестовой сессии"""
    async with dishka_container() as request_container:
        session = await request_container.get(AsyncSession)
        yield session

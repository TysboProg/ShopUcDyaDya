from typing import AsyncGenerator

import pytest_asyncio
from pytest_postgresql import factories
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

db_proc = factories.postgresql_noproc(
    port=5432, host="localhost", user="postgres", password="inal_2411"
)

postgresql = factories.postgresql(
    "db_proc",
)


@pytest_asyncio.fixture
async def async_engine(postgresql):
    db_uri = (
        f"postgresql+asyncpg://{postgresql.info.user}:{postgresql.info.password}"
        f"@{postgresql.info.host}:{postgresql.info.port}/"
        f"{postgresql.info.dbname}"
    )
    engine = create_async_engine(
        url=db_uri,
        echo=False,
        poolclass=StaticPool,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

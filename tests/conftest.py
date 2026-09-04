from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(image="postgres:18-alpine", dbname="shopucdyadya") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def apply_migrations(postgres_container):
    url = postgres_container.get_connection_url(driver="asyncpg")

    base_dir = Path(__file__).parent.parent
    alembic_cfg = Config(base_dir / "alembic.ini")

    alembic_cfg.set_main_option("sqlalchemy.url", url)

    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture(scope="session")
async def async_engine(postgres_container, apply_migrations) -> AsyncGenerator[AsyncEngine]:
    async_url = postgres_container.get_connection_url(driver="asyncpg")

    engine = create_async_engine(
        url=async_url,
        echo=False,
        poolclass=NullPool,
    )

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession]:
    async with async_engine.connect() as connection:
        transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        async with session_factory() as session:
            yield session

        await transaction.rollback()

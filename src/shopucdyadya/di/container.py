from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from shopucdyadya.di.providers import (
    DatabaseProvider,
    IntegrationProvider,
    RepositoryProvider,
    ServiceProvider,
)


def create_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(),
        IntegrationProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        FastapiProvider(),
    )


def setup_di(app: FastAPI) -> None:
    container = create_container()
    setup_dishka(container=container, app=app)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await app.state.dishka_container.close()

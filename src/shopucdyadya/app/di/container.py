from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from shopucdyadya.app.di.providers import (
    BrokerProvider,
    CacheProvider,
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
)


def create_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(),
        CacheProvider(),
        BrokerProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        FastapiProvider(),
    )


def setup_di(app: FastAPI) -> None:
    container = create_container()
    setup_dishka(container=container, app=app)

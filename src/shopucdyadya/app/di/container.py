from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.fastapi import FastapiProvider
from fastapi import FastAPI

from shopucdyadya.app.di.providers import (
    BrokerProvider,
    CacheProvider,
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
)


def _shared_providers() -> list[Provider]:
    return [
        DatabaseProvider(),
        CacheProvider(),
        BrokerProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    ]


def create_api_container(app: FastAPI) -> AsyncContainer:
    return make_async_container(
        *_shared_providers(),
        FastapiProvider(),
        context={FastAPI: app},
    )


def create_bot_container() -> AsyncContainer:
    return make_async_container(
        *_shared_providers(),
        AiogramProvider(),
    )

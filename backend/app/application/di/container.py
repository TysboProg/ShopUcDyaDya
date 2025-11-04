from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka, FastapiProvider
from fastapi import FastAPI

from .providers import (
    RepositoryProvider,
    DatabaseProvider,
    ServiceProvider,
    PromoValidatorProvider
)


def create_container():
    providers = [
        DatabaseProvider(),
        RepositoryProvider(),
        FastapiProvider(),
        ServiceProvider(),
        PromoValidatorProvider(),
    ]

    return make_async_container(*providers)


def setup_di(app: FastAPI):
    """Настройка DI для FastAPI приложения"""
    container = create_container()
    setup_dishka(container, app)
    return container
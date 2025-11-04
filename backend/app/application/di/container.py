from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from settings.config import settings

from .providers import DatabaseProvider, PromoValidatorProvider, RepositoryProvider, ServiceProvider


def create_container():
    providers = [
        DatabaseProvider(url=settings.db.url.encoded_string()),
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

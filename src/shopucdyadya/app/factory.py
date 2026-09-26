from pathlib import Path

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from shopucdyadya.app.cache import RateLimitHeaderMiddleware
from shopucdyadya.app.config import settings
from shopucdyadya.app.di.container import create_api_container
from shopucdyadya.app.lifespan import lifespan
from shopucdyadya.modules.webapp.router import router as webapp_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.openapi.title,
        version=settings.openapi.version,
        summary=settings.openapi.summary,
        description=settings.openapi.description,
        redoc_url=settings.openapi.redoc_url,
        docs_url=settings.openapi.doc_url,
        lifespan=lifespan,
    )

    container = create_api_container(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.app.allow_credentials,
        allow_methods=settings.app.allow_methods,
        allow_headers=settings.app.allow_headers,
    )

    app.add_middleware(
        RateLimitHeaderMiddleware,
    )

    app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).resolve().parent.parent / "static"),
        name="static",
    )

    setup_dishka(container=container, app=app)
    app.state.container = container

    register_routes(app)
    return app


def register_routes(app: FastAPI) -> None:
    app.include_router(webapp_router)

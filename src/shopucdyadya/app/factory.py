from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_fastapi import FastAPIRedis
from redis_fastapi import get_settings as get_redis_settings

from shopucdyadya.app.config import settings
from shopucdyadya.app.di.container import setup_di


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.openapi.title,
        version=settings.openapi.version,
        summary=settings.openapi.summary,
        description=settings.openapi.description,
        redoc_url=settings.openapi.redoc_url,
        docs_url=settings.openapi.doc_url,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.allow_origins,
        allow_credentials=settings.app.allow_credentials,
        allow_methods=settings.app.allow_methods,
        allow_headers=settings.app.allow_headers,
    )

    redis_settings = get_redis_settings()
    redis_settings.url = settings.cache_url.encoded_string()

    FastAPIRedis(app).lifespan().caching().rate_limiting()
    setup_di(app)

    register_routes(app)
    return app


def register_routes(app: FastAPI) -> None:
    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"message": "Hello World"}
    
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shopucdyadya.api.router import router
from shopucdyadya.core.config import settings
from shopucdyadya.di.container import lifespan, setup_di

app = FastAPI(
    lifespan=lifespan,
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

app.include_router(router)

setup_di(app)

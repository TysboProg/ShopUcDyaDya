from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_fastapi import FastAPIRedis

from shopucdyadya.app.config import settings
from shopucdyadya.app.di.container import setup_di

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

FastAPIRedis(app).lifespan().caching()


setup_di(app)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}

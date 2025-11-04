from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager
from loguru import logger

from api.routers import main_router
from api.exception_handler import register_exception_handlers
from application.di import setup_di


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI Lifespan")
    yield
    logger.info("Stopping FastAPI Lifespan",)

main_app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

setup_di(main_app)
register_exception_handlers(main_app)
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

main_app.include_router(main_router)

@main_app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


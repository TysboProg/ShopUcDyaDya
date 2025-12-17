import logging
from contextlib import asynccontextmanager

from api.exception_handler import register_exception_handlers
from api.routers import main_router
from application.di import setup_di
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI Lifespan")
    yield
    logger.info("Stopping FastAPI Lifespan")


main_app = FastAPI(lifespan=lifespan, docs_url="/docs", redoc_url="/redoc", title="API Дядюшки")
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(main_app)
setup_di(main_app)

main_app.include_router(main_router)

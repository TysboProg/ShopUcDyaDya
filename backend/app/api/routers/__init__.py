from fastapi import APIRouter

from .promocode import router as promocode_router

main_router = APIRouter()

main_router.include_router(promocode_router)

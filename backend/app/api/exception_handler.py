from fastapi import Request, FastAPI
from fastapi.responses import ORJSONResponse
from domain.exceptions.promo import (
    PromoCodeNotFoundException,
    PromoCodeAlreadyExistsException,
    PromoCodeExpiredException,
    PromoCodeAlreadyUsedException,
)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(PromoCodeNotFoundException)
    async def promo_not_found_handler(request: Request, exc: PromoCodeNotFoundException):
        return ORJSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(PromoCodeAlreadyExistsException)
    async def promo_already_exists_handler(request: Request, exc: PromoCodeAlreadyExistsException):
        return ORJSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(PromoCodeExpiredException)
    async def promo_expired_handler(request: Request, exc: PromoCodeExpiredException):
        return ORJSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(PromoCodeAlreadyUsedException)
    async def promo_already_used_handler(request: Request, exc: PromoCodeAlreadyUsedException):
        return ORJSONResponse(status_code=400, content={"detail": exc.message})
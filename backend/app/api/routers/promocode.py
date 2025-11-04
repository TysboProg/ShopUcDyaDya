from typing import Optional
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Query
)

from api.schemas import (
    PromoShortResponse,
    PromoListResponse,
    PromoResponse,
    MessageResponse,
    UsePromoResponse
)
from application.services import PromoService
from domain.enums import UcAmount, PromoStatus
from domain.exceptions.promo import (
    PromoCodeNotFoundException,
    PromoCodeAlreadyExistsException,
)

router = APIRouter(
    prefix="/promocode",
    tags=["Promocodes"],
    route_class=DishkaRoute
)

@router.post("/", response_model=PromoShortResponse)
async def create_promo(
        promo_service: FromDishka[PromoService],
        code: str,
        uc_amount: UcAmount,
        duration_days: int = Query(ge=1, le=365),
):
    """Создание нового промокода"""
    existing_promo = await promo_service.get_promo_by_code(code)
    if existing_promo:
        raise PromoCodeAlreadyExistsException(code=code)

    promo = await promo_service.create_promo(code, uc_amount, duration_days)
    return PromoShortResponse(
        id=UUID(promo.oid),
        code=promo.code,
        uc_amount=promo.uc_amount,
        expires_at=promo.expires_at,
        status=promo.status
    )


@router.get("/{promo_id}", response_model=PromoResponse)
async def get_promo(
        promo_service: FromDishka[PromoService],
        promo_id: UUID
):
    """Получение промокода по ID"""
    promo = await promo_service.get_promo(promo_id)
    if not promo:
        raise PromoCodeNotFoundException(code=str(promo_id))

    return PromoResponse(
        id=UUID(promo.oid),
        code=promo.code,
        uc_amount=promo.uc_amount,
        expires_at=promo.expires_at,
        status=promo.status,
        used_by=promo.usage.used_by,
        used_at=promo.usage.used_at
    )


@router.get("/code/{promo_code}", response_model=PromoResponse)
async def get_promo_by_code(
        promo_service: FromDishka[PromoService],
        promo_code: str
):
    """Получение промокода по коду"""
    promo = await promo_service.get_promo_by_code(promo_code)
    if not promo:
        raise PromoCodeNotFoundException(code=promo_code)

    return PromoResponse(
        id=UUID(promo.oid),
        code=promo.code,
        uc_amount=promo.uc_amount,
        expires_at=promo.expires_at,
        status=promo.status,
        used_by=promo.usage.used_by,
        used_at=promo.usage.used_at
    )


@router.get("/", response_model=PromoListResponse)
async def get_all_promos(
        promo_service: FromDishka[PromoService],
        uc_amount: Optional[UcAmount] = None,
        status: Optional[PromoStatus] = None,
        limit: Optional[int] = Query(None, ge=1, le=100),
        offset: Optional[int] = Query(None, ge=0)
):
    """Получение всех промокодов"""
    promos = await promo_service.get_all_promos(
        uc_amount=uc_amount.value if uc_amount else None,
        status=status.value if status else None,
        limit=limit,
        offset=offset
    )

    items = [PromoShortResponse(
        id=UUID(promo.oid),
        code=promo.code,
        uc_amount=promo.uc_amount,
        expires_at=promo.expires_at,
        status=promo.status
    ) for promo in promos]

    return PromoListResponse(items=items)


@router.post("/{promo_id}/use", response_model=UsePromoResponse)
async def use_promo(
        promo_service: FromDishka[PromoService],
        promo_id: UUID,
        user_id: str
):
    """Использование промокода"""
    promo = await promo_service.get_promo(promo_id)
    if not promo:
        raise PromoCodeNotFoundException(code=str(promo_id))

    await promo_service.use_promo(promo_id, user_id)
    return UsePromoResponse(
        message="Промокод успешно использован",
        uc_amount=promo.uc_amount.value
    )


@router.post("/code/{promo_code}/use", response_model=UsePromoResponse)
async def use_promo_by_code(
        promo_service: FromDishka[PromoService],
        promo_code: str,
        user_id: str
):
    """Использование промокода по коду"""
    promo = await promo_service.get_promo_by_code(promo_code)
    if not promo:
        raise PromoCodeNotFoundException(code=promo_code)

    await promo_service.use_promo(UUID(promo.oid), user_id)
    return UsePromoResponse(
        message="Промокод успешно использован",
        uc_amount=promo.uc_amount.value
    )


@router.delete("/{promo_id}", response_model=MessageResponse)
async def delete_promo(
        promo_service: FromDishka[PromoService],
        promo_id: UUID
):
    """Удаление промокода"""
    promo = await promo_service.get_promo(promo_id)
    if not promo:
        raise PromoCodeNotFoundException(code=str(promo_id))

    success = await promo_service.delete_promo(promo_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось удалить промокод"
        )

    return MessageResponse(message="Промокод успешно удален")
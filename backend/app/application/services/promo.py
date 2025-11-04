from typing import Optional, List
from uuid import UUID

from domain.entities.promo import PromoEntity
from domain.repositories.promo import PromoRepository
from domain.services import PromoValidator
from domain.enums import UcAmount, PromoStatus
from domain.exceptions.promo import (
    PromoCodeNotFoundException,
    PromoCodeAlreadyExistsException,
    PromoCodeExpiredException,
    PromoCodeAlreadyUsedException,
)


class PromoService:
    def __init__(
            self,
            promo_repository: PromoRepository,
            promo_validator: PromoValidator
    ) -> None:
        self.promo_repository = promo_repository
        self.promo_validator = promo_validator

    async def create_promo(
            self,
            code: str,
            uc_amount: UcAmount,
            duration_days: int
    ) -> PromoEntity:
        """Создание нового промокода"""
        # Проверяем, не существует ли уже промокод с таким кодом
        existing_promo = await self.promo_repository.get_by_code(code)
        if existing_promo:
            raise PromoCodeAlreadyExistsException(code=code)

        promo_entity = PromoEntity.create(
            code=code,
            uc_amount=uc_amount,
            duration_days=duration_days
        )

        await self.promo_repository.save(promo_entity)
        return promo_entity

    async def get_promo(self, promo_id: UUID) -> Optional[PromoEntity]:
        """Получение промокода по ID"""
        return await self.promo_repository.get_by_id(promo_id)

    async def get_promo_by_code(self, code: str) -> Optional[PromoEntity]:
        """Получение промокода по коду"""
        return await self.promo_repository.get_by_code(code)

    async def get_all_promos(
            self,
            uc_amount: Optional[str] = None,
            status: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[PromoEntity]:
        """Получение всех промокодов с фильтрацией"""
        return await self.promo_repository.get_all(
            uc_amount=uc_amount,
            status=status,
            limit=limit,
            offset=offset
        )

    async def use_promo(self, promo_id: UUID, user_id: str) -> PromoEntity:
        """Использование промокода"""
        promo_entity = await self.promo_repository.get_by_id(promo_id)
        if not promo_entity:
            raise PromoCodeNotFoundException(code=str(promo_id))

        try:
            promo_entity.use(user_id, self.promo_validator)
            await self.promo_repository.save(promo_entity)
            return promo_entity
        except ValueError as e:
            # Преобразуем стандартные ValueError в кастомные исключения
            error_msg = str(e).lower()
            if "expired" in error_msg:
                raise PromoCodeExpiredException(code=promo_entity.code)
            elif "used" in error_msg or "уже использован" in error_msg:
                raise PromoCodeAlreadyUsedException(code=promo_entity.code)
            else:
                raise ValueError(e)

    async def use_promo_by_code(self, code: str, user_id: str) -> PromoEntity:
        """Использование промокода по коду"""
        promo_entity = await self.promo_repository.get_by_code(code)
        if not promo_entity:
            raise PromoCodeNotFoundException(code=code)

        return await self.use_promo(UUID(promo_entity.oid), user_id)

    async def delete_promo(self, promo_id: UUID) -> bool:
        """Удаление промокода"""
        promo_entity = await self.promo_repository.get_by_id(promo_id)
        if not promo_entity:
            raise PromoCodeNotFoundException(code=str(promo_id))

        if not promo_entity.can_be_deleted():
            raise PromoCodeAlreadyUsedException(code=promo_entity.code)

        promo_entity.delete()
        return await self.promo_repository.delete(promo_id)

    async def expire_old_promos(self) -> List[PromoEntity]:
        """Помечаем просроченные промокоды"""
        all_promos = await self.promo_repository.get_all()
        expired_promos = []

        for promo in all_promos:
            if promo.status == PromoStatus.ACTIVE:
                promo.mark_expired()
                if promo.status == PromoStatus.EXPIRED:
                    await self.promo_repository.save(promo)
                    expired_promos.append(promo)

        return expired_promos
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import PromoEntity
from domain.repositories import PromoRepository
from domain.values import PromoValue, PromoCodeUsage, PromoCodeExpiration
from domain.enums import PromoStatus
from infra.db.models import Promocode


class PromoRepositoryImpl(PromoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, promo_entity: PromoEntity) -> None:
        """Сохранение промокода (создание или обновление)"""
        try:
            stmt = select(Promocode).where(Promocode.id == promo_entity.oid)
            result = await self.session.execute(stmt)
            existing_promo = result.scalar_one_or_none()

            if existing_promo:
                existing_promo.code = promo_entity.code
                existing_promo.uc_amount = promo_entity.uc_amount
                existing_promo.expires_at = promo_entity.expires_at
                existing_promo.status = promo_entity.status
                existing_promo.updated_at = datetime.now()

                if promo_entity.usage.used_at and promo_entity.usage.used_by:
                    existing_promo.used_at = promo_entity.usage.used_at
                    existing_promo.used_by = promo_entity.usage.used_by
            else:
                promo_model = Promocode(
                    code=promo_entity.code,
                    uc_amount=promo_entity.uc_amount,
                    expires_at=promo_entity.expires_at,
                    status=promo_entity.status,
                    created_at=promo_entity.created_at,
                )
                self.session.add(promo_model)

            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_by_id(self, promo_id: UUID) -> Optional[PromoEntity]:
        """Получение промокода по UUID"""
        stmt = select(Promocode).where(Promocode.id == promo_id)
        result = await self.session.execute(stmt)
        promo_model = result.scalar_one_or_none()

        if promo_model is None:
            return None

        return self._to_entity(promo_model)

    async def get_by_code(self, code: str) -> Optional[PromoEntity]:
        """Получение промокода по коду"""
        stmt = select(Promocode).where(Promocode.code == code)
        result = await self.session.execute(stmt)
        promo_model = result.scalar_one_or_none()

        if promo_model is None:
            return None

        return self._to_entity(promo_model)

    async def get_all(
            self,
            uc_amount: Optional[str] = None,
            status: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[PromoEntity]:
        """Получение списка промокодов с фильтрацией"""
        stmt = select(Promocode)

        conditions = []
        if uc_amount:
            conditions.append(Promocode.uc_amount == uc_amount)
        if status:
            conditions.append(Promocode.status == status)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        promo_models = result.scalars().all()

        return [self._to_entity(model) for model in promo_models]

    async def delete(self, promo_id: UUID) -> bool:
        """Удаление промокода"""
        try:
            stmt = select(Promocode).where(Promocode.id == promo_id)
            result = await self.session.execute(stmt)
            promo_model = result.scalar_one_or_none()

            if promo_model is None:
                return False

            await self.session.delete(promo_model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e

    @staticmethod
    def _to_entity(promo_model: Promocode) -> PromoEntity:
        """Преобразование модели SQLAlchemy в доменную сущность"""
        promo_code = PromoValue(
            code=promo_model.code,
            uc_amount=promo_model.uc_amount
        )

        expiration = PromoCodeExpiration(expires_at=promo_model.expires_at)

        usage = PromoCodeUsage(
            used_at=getattr(promo_model, 'used_at', None),
            used_by=getattr(promo_model, 'used_by', None)
        )

        promo_entity = PromoEntity(
            promo_code=promo_code,
            expiration=expiration,
            usage=usage,
            status=PromoStatus(promo_model.status.value) if hasattr(promo_model.status, 'value') else PromoStatus(promo_model.status),
            created_at=promo_model.created_at,
        )

        return promo_entity
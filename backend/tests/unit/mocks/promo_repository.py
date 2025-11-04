from unittest.mock import AsyncMock
from typing import Optional, List
from uuid import UUID
from domain.entities.promo import PromoEntity
from domain.repositories.promo import PromoRepository


class MockPromoRepository(PromoRepository):
    """Мок репозитория промокодов для unit-тестов"""

    def __init__(self):
        self.promos = {}
        self.save = AsyncMock()
        self.get_by_id = AsyncMock()
        self.get_by_code = AsyncMock()
        self.get_all = AsyncMock()
        self.delete = AsyncMock()

    async def save(self, promo_entity: PromoEntity) -> None:
        self.promos[promo_entity.oid] = promo_entity
        self.save.return_value = None

    async def get_by_id(self, pid: UUID) -> Optional[PromoEntity]:
        return self.get_by_id.return_value

    async def get_by_code(self, code: str) -> Optional[PromoEntity]:
        return self.get_by_code.return_value

    async def get_all(
            self,
            uc_amount: Optional[str] = None,
            status: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[PromoEntity]:
        return self.get_all.return_value

    async def delete(self, pid: UUID) -> bool:
        return self.delete.return_value
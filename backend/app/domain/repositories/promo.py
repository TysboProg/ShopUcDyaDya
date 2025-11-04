from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from domain.entities.promo import PromoEntity


class PromoRepository(ABC):
    @abstractmethod
    async def save(self, promo_entity: PromoEntity) -> None:
        """Сохранение промокода"""

    @abstractmethod
    async def get_by_id(self, pid: UUID) -> Optional[PromoEntity]:
        """Получение промокода по ID"""

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[PromoEntity]:
        """Получение промокода по коду"""

    @abstractmethod
    async def get_all(
            self,
            uc_amount: Optional[str] = None,
            status: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[PromoEntity]:
        """Получение списка промокодов с фильтрацией"""

    @abstractmethod
    async def delete(self, pid: UUID) -> bool:
        """Удаление промокода"""
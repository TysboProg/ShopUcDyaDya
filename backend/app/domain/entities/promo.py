from dataclasses import dataclass, field
from datetime import datetime

from domain.entities.base import BaseEntity
from domain.enums import PromoStatus, UcAmount
from domain.events import CreatedPromoCodeEvent, DeletedPromoCodeEvent
from domain.services import PromoValidator
from domain.values.promo import PromoCodeExpiration, PromoCodeUsage, PromoValue


@dataclass
class PromoEntity(BaseEntity):
    promo_code: PromoValue
    expiration: PromoCodeExpiration
    usage: PromoCodeUsage = field(default_factory=PromoCodeUsage)
    status: PromoStatus = PromoStatus.ACTIVE

    @classmethod
    def create(cls, code: str, uc_amount: UcAmount, duration_days: int) -> "PromoEntity":
        if not code:
            raise ValueError("Код промокода не может быть пустым")

        new_promo = cls(
            promo_code=PromoValue(code=code, uc_amount=uc_amount),
            expiration=PromoCodeExpiration.create(duration_days),
            status=PromoStatus.ACTIVE,
        )
        new_promo.register_event(CreatedPromoCodeEvent(code=code))
        return new_promo

    def use(self, user_id: str, validator: PromoValidator) -> None:
        validator.validate_for_use(self)

        self.usage = self.usage.mark_used(user_id)
        self.status = PromoStatus.USED

    def mark_expired(self) -> None:
        if self.expiration.is_expired:
            self.status = PromoStatus.EXPIRED

    def can_be_deleted(self) -> bool:
        return self.status != PromoStatus.USED

    def delete(self) -> None:
        if not self.can_be_deleted():
            raise ValueError("Использованный промокод нельзя удалить")

        self.register_event(DeletedPromoCodeEvent(code=self.promo_code.code))

    @property
    def code(self) -> str:
        return self.promo_code.code

    @property
    def uc_amount(self) -> UcAmount:
        return self.promo_code.uc_amount

    @property
    def expires_at(self) -> datetime:
        return self.expiration.expires_at

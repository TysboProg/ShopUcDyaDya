from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.exceptions.promo import (
    PromoCodeExpiredException,
    PromoCodeAlreadyUsedException
)
from domain.enums import PromoStatus

if TYPE_CHECKING:
    from domain.entities.promo import PromoEntity


@dataclass
class PromoValidator:
    @staticmethod
    def validate_for_use(promo_entity: 'PromoEntity') -> None:
        if promo_entity.status != PromoStatus.ACTIVE:
            raise PromoCodeAlreadyUsedException(promo_entity.code)

        if promo_entity.expiration.is_expired:
            promo_entity.status = PromoStatus.EXPIRED
            raise PromoCodeExpiredException(promo_entity.code)
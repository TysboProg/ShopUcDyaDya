from unittest.mock import Mock

import pytest
from domain.enums import PromoStatus
from domain.exceptions.promo import PromoCodeAlreadyUsedException, PromoCodeExpiredException
from domain.services import PromoValidator


class TestPromoValidator:
    """Тесты для валидатора промокодов"""

    def test_validate_active_promo(self, active_promo_mock):
        """Валидация активного промокода не вызывает исключений"""
        PromoValidator.validate_for_use(active_promo_mock)

    def test_validate_expired_promo(self, expired_promo_mock):
        """Валидация просроченного промокода вызывает исключение"""
        with pytest.raises(PromoCodeExpiredException):
            PromoValidator.validate_for_use(expired_promo_mock)

        assert expired_promo_mock.status == PromoStatus.EXPIRED

    def test_validate_used_promo(self, used_promo_mock):
        """Валидация использованного промокода вызывает исключение"""
        with pytest.raises(PromoCodeAlreadyUsedException):
            PromoValidator.validate_for_use(used_promo_mock)

        assert used_promo_mock.status == PromoStatus.USED

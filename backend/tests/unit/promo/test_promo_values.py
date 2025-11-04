from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from domain.enums import UcAmount
from domain.values.promo import PromoCodeExpiration, PromoCodeUsage, PromoValue


class TestPromoValue:
    """Тесты для значения промокода"""

    def test_create_valid_promo_value(self):
        """Создание валидного промокода"""
        promo_value = PromoValue(code="TEST123", uc_amount=UcAmount.UC300)

        assert promo_value.code == "TEST123"
        assert promo_value.uc_amount == UcAmount.UC300

    def test_create_empty_code_raises_error(self):
        """Создание промокода с пустым кодом вызывает ошибку"""
        with pytest.raises(ValueError, match="Промокод не может быть пустым"):
            PromoValue(code="", uc_amount=UcAmount.UC300)

    def test_create_whitespace_code_raises_error(self):
        """Создание промокода с кодом из пробелов вызывает ошибку"""
        with pytest.raises(ValueError, match="Промокод не может быть пустым"):
            PromoValue(code="   ", uc_amount=UcAmount.UC300)

    def test_create_without_uc_amount_raises_error(self):
        """Создание промокода без номинала UC вызывает ошибку"""
        with pytest.raises(ValueError, match="Номинал UC не может быть пустым"):
            PromoValue(code="TEST123", uc_amount=None)


class TestPromoCodeExpiration:
    """Тесты для срока действия промокода"""

    def test_create_expiration(self):
        """Создание срока действия"""
        expiration = PromoCodeExpiration.create(duration_days=7)

        assert expiration.expires_at > datetime.now(timezone.utc)
        assert expiration.expires_at <= datetime.now(timezone.utc) + timedelta(days=7)

    def test_create_with_negative_days_raises_error(self):
        """Создание с отрицательной продолжительностью вызывает ошибку"""
        with pytest.raises(ValueError, match="Продолжительность дней должна быть положительной"):
            PromoCodeExpiration.create(duration_days=-1)

    def test_create_with_zero_days_raises_error(self):
        """Создание с нулевой продолжительностью вызывает ошибку"""
        with pytest.raises(ValueError, match="Продолжительность дней должна быть положительной"):
            PromoCodeExpiration.create(duration_days=0)

    def test_is_expired_when_not_expired(self):
        """Проверка, что не просроченный промокод не считается просроченным"""
        expiration = PromoCodeExpiration(expires_at=datetime.now(timezone.utc) + timedelta(days=1))

        assert not expiration.is_expired

    def test_is_expired_when_expired(self):
        """Проверка, что просроченный промокод считается просроченным"""
        expiration = PromoCodeExpiration(expires_at=datetime.now(timezone.utc) - timedelta(days=1))

        assert expiration.is_expired


class TestPromoCodeUsage:
    """Тесты для использования промокода"""

    def test_create_default_usage(self):
        """Создание использования по умолчанию"""
        usage = PromoCodeUsage()

        assert usage.used_at is None
        assert usage.used_by is None

    def test_mark_used(self):
        """Пометка промокода как использованного"""
        user_id = uuid4()
        usage = PromoCodeUsage.mark_used(user_id)

        assert usage.used_by == user_id
        assert usage.used_at is not None
        assert usage.used_at <= datetime.now(timezone.utc)

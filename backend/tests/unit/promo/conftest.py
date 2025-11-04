from unittest.mock import AsyncMock

import pytest
from domain.entities import PromoEntity
from domain.enums import PromoStatus, UcAmount
from domain.services import PromoValidator


@pytest.fixture
def promo_validator():
    return PromoValidator()


@pytest.fixture
def active_promo_entity():
    """Создание активного промокода"""
    return PromoEntity.create(code="TEST123", uc_amount=UcAmount.UC300, duration_days=7)


@pytest.fixture
def active_promo_mock():
    """Мок активного промокода"""
    mock = AsyncMock()
    mock.status = PromoStatus.ACTIVE
    mock.code = "ACTIVE123"
    mock.expiration.is_expired = False
    return mock


@pytest.fixture
def expired_promo_mock():
    """Мок просроченного промокода"""
    mock = AsyncMock()
    mock.status = PromoStatus.ACTIVE
    mock.code = "EXPIRED123"
    mock.expiration.is_expired = True
    return mock


@pytest.fixture
def used_promo_mock():
    """Мок использованного промокода"""
    mock = AsyncMock()
    mock.status = PromoStatus.USED
    mock.code = "USED123"
    mock.expiration.is_expired = False
    return mock

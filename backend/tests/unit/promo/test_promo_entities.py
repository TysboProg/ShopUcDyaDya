import pytest
from datetime import datetime, timezone, timedelta

from domain.entities.promo import PromoEntity
from domain.enums import UcAmount, PromoStatus
from domain.events import DeletedPromoCodeEvent
from domain.values.promo import PromoValue, PromoCodeExpiration
from domain.exceptions.promo import PromoCodeExpiredException, PromoCodeAlreadyUsedException
from domain.services import PromoValidator


class TestPromoEntity:
    """Тесты для сущности промокода"""

    @pytest.fixture
    def promo_validator(self):
        return PromoValidator()

    @pytest.fixture
    def active_promo_entity(self):
        """Создание активного промокода"""
        return PromoEntity.create(
            code="TEST123",
            uc_amount=UcAmount.UC300,
            duration_days=7
        )

    def test_create_promo_entity(self):
        """Создание сущности промокода"""
        promo = PromoEntity.create(
            code="NEW123",
            uc_amount=UcAmount.UC600,
            duration_days=14
        )

        assert promo.code == "NEW123"
        assert promo.uc_amount == UcAmount.UC600
        assert promo.status == PromoStatus.ACTIVE
        assert len(promo.events) == 1

        assert promo.expires_at > datetime.now(timezone.utc)
        assert promo.expires_at <= datetime.now(timezone.utc) + timedelta(days=14)

    def test_create_with_empty_code_raises_error(self):
        """Создание с пустым кодом вызывает ошибку"""
        with pytest.raises(ValueError, match="Код промокода не может быть пустым"):
            PromoEntity.create(code="", uc_amount=UcAmount.UC300, duration_days=7)

    def test_use_active_promo(self, active_promo_entity, promo_validator):
        """Использование активного промокода"""
        user_id = "user-123"

        active_promo_entity.use(user_id, promo_validator)

        assert active_promo_entity.status == PromoStatus.USED
        assert active_promo_entity.usage.used_by == user_id
        assert active_promo_entity.usage.used_at is not None

    def test_use_expired_promo(self, promo_validator):
        """Попытка использования просроченного промокода"""
        promo = PromoEntity(
            promo_code=PromoValue(code="EXPIRED", uc_amount=UcAmount.UC300),
            expiration=PromoCodeExpiration(
                expires_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            status=PromoStatus.ACTIVE
        )

        with pytest.raises(PromoCodeExpiredException):
            promo.use("user-123", promo_validator)

        assert promo.status == PromoStatus.EXPIRED

    def test_use_already_used_promo(self, active_promo_entity, promo_validator):
        """Попытка использования уже использованного промокода"""
        user_id = "user-123"
        active_promo_entity.use(user_id, promo_validator)

        with pytest.raises(PromoCodeAlreadyUsedException):
            active_promo_entity.use("user-456", promo_validator)

    def test_mark_expired_when_not_expired(self, active_promo_entity):
        """Пометка как просроченного, когда срок не истек"""
        active_promo_entity.mark_expired()

        assert active_promo_entity.status == PromoStatus.ACTIVE

    def test_mark_expired_when_expired(self):
        """Пометка как просроченного, когда срок истек"""
        promo = PromoEntity(
            promo_code=PromoValue(code="EXPIRED", uc_amount=UcAmount.UC300),
            expiration=PromoCodeExpiration(
                expires_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            status=PromoStatus.ACTIVE
        )

        promo.mark_expired()

        assert promo.status == PromoStatus.EXPIRED

    def test_can_be_deleted_when_active(self, active_promo_entity):
        """Активный промокод можно удалить"""
        assert active_promo_entity.can_be_deleted() is True

    def test_can_be_deleted_when_expired(self):
        """Просроченный промокод можно удалить"""
        promo = PromoEntity(
            promo_code=PromoValue(code="EXPIRED", uc_amount=UcAmount.UC300),
            expiration=PromoCodeExpiration(
                expires_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            status=PromoStatus.EXPIRED
        )

        assert promo.can_be_deleted() is True

    def test_can_be_deleted_when_used(self, active_promo_entity, promo_validator):
        """Использованный промокод нельзя удалить"""
        active_promo_entity.use("user-123", promo_validator)

        assert active_promo_entity.can_be_deleted() is False

    def test_delete_active_promo(self, active_promo_entity):
        """Удаление активного промокода"""
        initial_events_count = len(active_promo_entity.events)

        active_promo_entity.delete()

        assert len(active_promo_entity.events) == initial_events_count + 1

        last_event = active_promo_entity.events[-1]
        assert isinstance(last_event, DeletedPromoCodeEvent)
        assert last_event.code == active_promo_entity.code

    def test_delete_used_promo_raises_error(self, active_promo_entity, promo_validator):
        """Удаление использованного промокода вызывает ошибку"""
        active_promo_entity.use("user-123", promo_validator)

        with pytest.raises(ValueError, match="Использованный промокод нельзя удалить"):
            active_promo_entity.delete()

    def test_properties(self, active_promo_entity):
        """Проверка свойств сущности"""
        assert active_promo_entity.code == "TEST123"
        assert active_promo_entity.uc_amount == UcAmount.UC300
        assert active_promo_entity.expires_at is not None
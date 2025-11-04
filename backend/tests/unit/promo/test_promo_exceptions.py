from domain.exceptions.promo import (
    PromoCodeAlreadyExistsException,
    PromoCodeAlreadyUsedException,
    PromoCodeExpiredException,
    PromoCodeNotFoundException,
)


class TestPromoExceptions:
    """Тесты для исключений промокодов"""

    def test_promo_code_not_found_exception(self):
        """Исключение 'промокод не найден'"""
        exception = PromoCodeNotFoundException(code="NOTFOUND")

        assert exception.code == "NOTFOUND"
        assert exception.message == "Промокод NOTFOUND не найден"

    def test_promo_code_already_exists_exception(self):
        """Исключение 'промокод уже существует'"""
        exception = PromoCodeAlreadyExistsException(code="EXISTS")

        assert exception.code == "EXISTS"
        assert exception.message == "Промокод EXISTS уже существует"

    def test_promo_code_expired_exception(self):
        """Исключение 'промокод просрочен'"""
        exception = PromoCodeExpiredException(code="EXPIRED")

        assert exception.code == "EXPIRED"
        assert exception.message == "Промокод EXPIRED просрочен"

    def test_promo_code_already_used_exception(self):
        """Исключение 'промокод уже использован'"""
        exception = PromoCodeAlreadyUsedException(code="USED")

        assert exception.code == "USED"
        assert exception.message == "Промокод USED уже использован"

from application.services import PromoService
from dishka import Provider, Scope, provide
from domain.repositories.promo import PromoRepository
from domain.services import PromoValidator


class PromoValidatorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_promo_validator(self) -> PromoValidator:
        return PromoValidator()


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_promo_service(
        self, promo_repository: PromoRepository, promo_validator: PromoValidator
    ) -> PromoService:
        return PromoService(promo_repository, promo_validator)

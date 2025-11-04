from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.promo import PromoRepository
from domain.services import PromoValidator
from infra.db.repositories import PromoRepositoryImpl


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_promo_repository(
            self,
            session: AsyncSession
    ) -> PromoRepository:
        return PromoRepositoryImpl(session)
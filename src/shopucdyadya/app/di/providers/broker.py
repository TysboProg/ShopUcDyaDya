from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide

from shopucdyadya.infra.broker import PgQueuerBroker, broker


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_broker(self) -> AsyncGenerator[PgQueuerBroker]:
        await broker.start()
        yield broker
        await broker.shutdown()

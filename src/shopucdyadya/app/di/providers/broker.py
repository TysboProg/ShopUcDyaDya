from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from taskiq_aio_pika import AioPikaBroker

from shopucdyadya.infra.broker import broker


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_broker(self) -> AsyncGenerator[AioPikaBroker]:
        yield broker
        await broker.shutdown()

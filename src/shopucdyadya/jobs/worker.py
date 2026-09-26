from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from pgqueuer import PgQueuer

from shopucdyadya.infra.broker import broker
from shopucdyadya.jobs import tasks  # noqa: F401  # register task decorators


@asynccontextmanager
async def main() -> AsyncGenerator[PgQueuer]:
    """Factory for ``pgq run shopucdyadya.jobs.worker:main``."""

    await broker.start()
    try:
        yield broker.pgq
    finally:
        await broker.shutdown()

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import psycopg
from pgqueuer.models import Schedule
from pgqueuer.sm import SchedulerManager

from shopucdyadya.app.config import settings
from shopucdyadya.infra.scheduler import scheduler

logger = logging.getLogger(__name__)


@scheduler.schedule("cleanup_rate_limits", "*/15 * * * *")
async def cleanup_rate_limits(schedule: Schedule) -> None:
    del schedule
    dsn = (
        settings.require_runtime_db_url()
        .unicode_string()
        .replace("postgresql+psycopg://", "postgresql://", 1)
    )
    async with await psycopg.AsyncConnection.connect(dsn, autocommit=True) as connection:
        result = await connection.execute(
            "DELETE FROM rate_limits WHERE window_start < %s",
            (int(time.time()) - 86400,),
        )
        logger.info("Removed %s expired rate-limit rows", result.rowcount)


@asynccontextmanager
async def main() -> AsyncGenerator[SchedulerManager]:
    """Entrypoint for ``pgq run shopucdyadya.jobs.scheduler:main``."""
    await scheduler.start()
    try:
        yield scheduler.sm
    finally:
        await scheduler.shutdown()

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import psycopg
from pgqueuer.db import PsycopgDriver
from pgqueuer.models import Schedule
from pgqueuer.queries import Queries
from pgqueuer.sm import SchedulerManager

from shopucdyadya.app.config import settings

type ScheduleHandler = Callable[[Schedule], Awaitable[None]]


@dataclass(slots=True)
class PgQueuerScheduledTask:
    name: str
    expression: str
    scheduler: PgQueuerScheduler
    function: ScheduleHandler

    async def __call__(self, schedule: Schedule) -> None:
        await self.function(schedule)


class PgQueuerScheduler:
    """Taskiq-like cron scheduler facade backed only by PostgreSQL."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._connection: psycopg.AsyncConnection | None = None
        self._sm: SchedulerManager | None = None
        self._tasks: dict[str, PgQueuerScheduledTask] = {}

    @property
    def sm(self) -> SchedulerManager:
        if self._sm is None:
            raise RuntimeError("PgQueuerScheduler is not started")
        return self._sm

    def schedule(
        self,
        name: str,
        expression: str,
    ) -> Callable[[ScheduleHandler], PgQueuerScheduledTask]:
        def decorator(function: ScheduleHandler) -> PgQueuerScheduledTask:
            if name in self._tasks:
                raise ValueError(f"Schedule {name!r} is already registered")
            task = PgQueuerScheduledTask(name, expression, self, function)
            self._tasks[name] = task
            return task

        return decorator

    async def start(self) -> None:
        if self._sm is not None:
            return
        connection: psycopg.AsyncConnection | None = None
        try:
            connection = await psycopg.AsyncConnection.connect(self._dsn, autocommit=True)
            self._connection = connection
            driver = PsycopgDriver(connection)
            self._sm = SchedulerManager(Queries(driver))
            for task in self._tasks.values():
                self._register(task)
        except Exception:
            if connection is not None:
                await connection.close()
            self._connection = None
            self._sm = None
            raise

    def _register(self, task: PgQueuerScheduledTask) -> None:
        @self.sm.schedule(task.name, task.expression)
        async def handle(schedule: Schedule) -> None:
            await task.function(schedule)

    async def run(self) -> None:
        await self.start()
        await self.sm.run()

    async def shutdown(self) -> None:
        if self._connection is not None:
            await self._connection.close()
        self._connection = None
        self._sm = None


scheduler = PgQueuerScheduler(
    settings.require_runtime_db_url()
    .unicode_string()
    .replace("postgresql+psycopg://", "postgresql://", 1)
)

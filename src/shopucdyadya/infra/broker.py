from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import ParamSpec, TypeVar, cast

import psycopg
from pgqueuer import DatabaseRetryEntrypointExecutor, Job, PgQueuer
from pgqueuer.db import PsycopgDriver

from shopucdyadya.app.config import settings

P = ParamSpec("P")
R = TypeVar("R")
type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
type Handler = Callable[..., Awaitable[object]]


@dataclass(slots=True)
class PgQueuerTask:
    name: str
    broker: PgQueuerBroker
    function: Handler

    async def kiq(self, *args: object, priority: int = 0, **kwargs: object) -> object:
        return await self.broker.enqueue(self.name, args, kwargs, priority=priority)

    async def __call__(self, *args: object, **kwargs: object) -> object:
        return await self.function(*args, **kwargs)


class PgQueuerBroker:
    """Taskiq-like producer/consumer facade backed only by PostgreSQL."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._connection: psycopg.AsyncConnection | None = None
        self._pgq: PgQueuer | None = None
        self._tasks: dict[str, PgQueuerTask] = {}

    @property
    def pgq(self) -> PgQueuer:
        if self._pgq is None:
            raise RuntimeError("PgQueuerBroker is not started")
        return self._pgq

    def task(self, name: str | None = None) -> Callable[[Callable[P, Awaitable[R]]], PgQueuerTask]:
        def decorator(function: Callable[P, Awaitable[R]]) -> PgQueuerTask:
            task_name = name or f"{function.__module__}:{function.__qualname__}"
            task = PgQueuerTask(task_name, self, cast(Handler, function))
            if task_name in self._tasks:
                raise ValueError(f"Task {task_name!r} is already registered")
            self._tasks[task_name] = task
            return task

        return decorator

    async def start(self) -> None:
        if self._pgq is not None:
            return
        connection: psycopg.AsyncConnection | None = None
        try:
            connection = await psycopg.AsyncConnection.connect(self._dsn, autocommit=True)
            self._connection = connection
            self._pgq = PgQueuer(PsycopgDriver(connection))
            for task in self._tasks.values():
                self._register(task)
        except Exception:
            if connection is not None:
                await connection.close()
            self._connection = None
            self._pgq = None
            raise

    def _register(self, task: PgQueuerTask) -> None:
        @self.pgq.entrypoint(
            task.name,
            executor_factory=lambda parameters: DatabaseRetryEntrypointExecutor(
                parameters=parameters,
                max_attempts=3,
                initial_delay=timedelta(seconds=1),
            ),
        )
        async def handle(job: Job) -> None:
            payload = cast(JsonObject, json.loads((job.payload or b"{}").decode("utf-8")))
            raw_args = payload.get("args")
            raw_kwargs = payload.get("kwargs")
            if not isinstance(raw_args, list):
                raise TypeError("Task payload args must be a JSON array")
            if not isinstance(raw_kwargs, dict):
                raise TypeError("Task payload kwargs must be a JSON object")
            args = tuple(raw_args)
            kwargs: dict[str, object] = {}
            for key, value in raw_kwargs.items():
                if not isinstance(key, str):
                    raise TypeError("Task payload kwargs keys must be strings")
                kwargs[key] = value
            await task.function(*args, **kwargs)

    async def enqueue(
        self,
        name: str,
        args: tuple[object, ...],
        kwargs: dict[str, object],
        *,
        priority: int = 0,
    ) -> object:
        if self._pgq is None:
            await self.start()
        payload = json.dumps({"args": args, "kwargs": kwargs}, separators=(",", ":")).encode()
        job_ids = await self.pgq.qm.queries.enqueue([name], [payload], [priority])
        return job_ids[0]

    async def is_ready(self) -> bool:
        await self.start()
        query = """
            SELECT to_regclass('pgqueuer') IS NOT NULL
               AND to_regtype('pgqueuer_status') IS NOT NULL
        """
        if self._connection is not None:
            result = await self._connection.execute(query)
            row = await result.fetchone()
            return bool(row[0]) if row else False
        return False

    async def run(self) -> None:
        await self.pgq.run()

    async def shutdown(self) -> None:
        if self._connection is not None:
            await self._connection.close()
        self._connection = None
        self._pgq = None


broker = PgQueuerBroker(
    settings.require_runtime_db_url()
    .unicode_string()
    .replace("postgresql+psycopg://", "postgresql://", 1)
)

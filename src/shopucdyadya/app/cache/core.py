from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import timedelta

from psycache import AsyncPostgresCache
from psycache.sqlalchemy import AsyncSQLAlchemyCachePool
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .types import JsonObject


@dataclass(slots=True)
class RateLimitConfig:
    count: int
    window_seconds: int
    scope: str | None = None

    @property
    def key_suffix(self) -> str:
        return self.scope or "default"


@dataclass(slots=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    limit: int
    retry_after: int  # секунды до сброса окна


class PgCache:
    """Framework-agnostic кэш и rate limiter на PostgreSQL."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._cache = AsyncPostgresCache(AsyncSQLAlchemyCachePool(engine))
        self._cache_initialized = False
        self._cache_init_lock = asyncio.Lock()

    async def _ensure_cache_table(self) -> None:
        if self._cache_initialized:
            return

        async with self._cache_init_lock:
            if not self._cache_initialized:
                async with self._engine.connect() as connection:
                    await connection.execute(text("SELECT 1 FROM psycache LIMIT 1"))
                self._cache_initialized = True

    async def is_available(self) -> bool:
        await self._ensure_cache_table()
        async with self._engine.connect() as connection:
            await connection.execute(text("SELECT 1 FROM psycache LIMIT 1"))
        return True

    async def get(self, key: str) -> JsonObject | None:
        await self._ensure_cache_table()
        return await self._cache.get_raw(key)

    async def set(self, key: str, value: JsonObject, ttl: int | timedelta) -> None:
        await self._ensure_cache_table()
        await self._cache.put_raw(key, value, ttl=ttl)

    async def delete(self, key: str) -> None:
        await self._ensure_cache_table()
        await self._cache.remove(key)

    # ── Rate limiting (framework-agnostic) ───────────────────────────────
    async def check_rate_limit(self, limit: RateLimitConfig, identity: str) -> RateLimitResult:
        key = f"ratelimit:{limit.key_suffix}:{identity}"
        now = int(time.time())
        window_start = now - (now % limit.window_seconds)

        async with self._engine.begin() as conn:
            row = await conn.execute(
                text("""
                    INSERT INTO rate_limits (key, window_start, count)
                    VALUES (:key, :window_start, 1)
                    ON CONFLICT (key) DO UPDATE
                    SET
                        count = CASE
                            WHEN rate_limits.window_start + :window <= :now
                                THEN 1
                            ELSE rate_limits.count + 1
                        END,
                        window_start = CASE
                            WHEN rate_limits.window_start + :window <= :now
                                THEN :window_start
                            ELSE rate_limits.window_start
                        END
                    RETURNING count, window_start
                """),
                {
                    "key": key,
                    "window_start": window_start,
                    "window": limit.window_seconds,
                    "now": now,
                },
            )
            count, ws = row.one()

        retry_after = max(0, (ws + limit.window_seconds) - now)
        return RateLimitResult(
            allowed=count <= limit.count,
            remaining=max(0, limit.count - count),
            limit=limit.count,
            retry_after=retry_after,
        )

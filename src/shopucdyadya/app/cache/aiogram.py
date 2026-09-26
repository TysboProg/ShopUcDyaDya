from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

from .core import PgCache, RateLimitConfig
from .types import JsonObject


@dataclass(slots=True)
class AiogramCache:
    """Хелпер для работы с кэшем и лимитами в aiogram-хендлерах."""

    core: PgCache

    async def get(self, key: str) -> JsonObject | None:
        return await self.core.get(key)

    async def set(self, key: str, value: JsonObject, ttl: int | timedelta) -> None:
        await self.core.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> None:
        await self.core.delete(key)

    async def get_str(self, key: str) -> str | None:
        value = await self.core.get(key)
        if value is None:
            return None
        text = value.get("text")
        return text if isinstance(text, str) else None

    async def set_str(
        self,
        key: str,
        text: str,
        ttl: int | timedelta,
    ) -> None:
        await self.core.set(key, {"text": text}, ttl=ttl)

    async def check_rate_limit(self, limit: RateLimitConfig, user: User) -> bool:
        """True — можно обрабатывать, False — лимит исчерпан."""
        result = await self.core.check_rate_limit(limit, f"tg:{user.id}")
        return result.allowed


class AiogramRateLimitMiddleware(BaseMiddleware):
    """Пример middleware, который можно навесить на роутер."""

    def __init__(self, cache: AiogramCache, limit: RateLimitConfig) -> None:
        self._cache = cache
        self._limit = limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> object:
        user: User | None = data.get("event_from_user")
        if user is not None:
            allowed = await self._cache.check_rate_limit(self._limit, user)
            if not allowed:
                if isinstance(event, Message):
                    await event.answer("Слишком много запросов, попробуйте позже.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Слишком много запросов.", show_alert=True)
                return None
        return await handler(event, data)

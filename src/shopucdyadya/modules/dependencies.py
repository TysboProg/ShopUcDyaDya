import time

from aiogram.utils.web_app import safe_parse_webapp_init_data
from dishka.integrations.fastapi import inject
from dishka.integrations.aiogram import FromDishka
from fastapi import HTTPException, Request, status

from shopucdyadya.app.cache import PgCache, RateLimitConfig
from shopucdyadya.app.config import settings


def telegram_user_id(request: Request) -> int | None:
    cached = getattr(request.state, "telegram_user_id", None)
    if isinstance(cached, int):
        return cached

    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        return None

    if settings.bot_token is None:
        raise RuntimeError("BOT_TOKEN must be configured to validate Telegram initData")

    try:
        data = safe_parse_webapp_init_data(
            token=settings.bot_token.get_secret_value(),
            init_data=init_data,
        )
    except ValueError as error:
        raise HTTPException(401, "Telegram WebApp signature mismatch") from error

    now = int(time.time())
    auth_ts = int(data.auth_date.timestamp())
    if auth_ts > now + 60 or now - auth_ts > 86400:
        raise HTTPException(401, "Telegram WebApp data expired")

    if data.user is None:
        raise HTTPException(401, "Telegram WebApp data missing user")

    user_id = data.user.id
    request.state.telegram_user_id = user_id
    return user_id


def require_telegram_user_id(request: Request) -> int:
    user_id = telegram_user_id(request)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram WebApp authentication is required",
        )
    return user_id


@inject
async def rate_limit(
    request: Request,
    cache: FromDishka[PgCache],
    scope: str = "api",
) -> None:
    user_id = telegram_user_id(request)
    identity = (
        f"tg:{user_id}"
        if user_id is not None
        else f"ip:{request.client.host if request.client else 'unknown'}"
    )

    result = await cache.check_rate_limit(
        RateLimitConfig(
            count=30,
            window_seconds=60,
            scope=scope,
        ),
        identity,
    )

    request.state.rate_limit_remaining = {
        scope: result.remaining,
    }

    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many {scope} requests",
            headers={
                "Retry-After": str(result.retry_after),
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": "0",
            },
        )

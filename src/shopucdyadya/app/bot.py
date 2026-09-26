import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from dishka import FromDishka
from dishka.integrations.aiogram import inject, setup_dishka

from shopucdyadya.app.cache import AiogramCache, AiogramRateLimitMiddleware, RateLimitConfig
from shopucdyadya.app.config import settings
from shopucdyadya.app.di.container import create_bot_container

dp = Dispatcher()


def _webapp_keyboard() -> InlineKeyboardMarkup | None:
    if settings.webapp_url is None:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть магазин",
                    web_app=WebAppInfo(url=settings.webapp_url.encoded_string()),
                )
            ]
        ]
    )


@dp.message(
    CommandStart(),
)
@inject
async def command_start_handler(
    message: Message,
    cache: FromDishka[AiogramCache],
) -> None:
    assert message.from_user is not None
    allowed = await cache.check_rate_limit(
        RateLimitConfig(count=5, window_seconds=60, scope="start"), message.from_user
    )
    if not allowed:
        await message.answer("Слишком много запросов, попробуйте позже.")
        return

    keyboard = _webapp_keyboard()
    cached = await cache.get_str(f"user:{message.from_user.id}:greeting")
    if cached is not None:
        await message.answer(cached, reply_markup=keyboard)
        return
    text = f"Hello, {html.bold(message.from_user.full_name)}!"
    await cache.set_str(f"user:{message.from_user.id}:greeting", text, ttl=3600)
    await message.answer(text, reply_markup=keyboard)


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def _run() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    container = create_bot_container()  # ← создаём один раз

    if settings.bot_token is None:
        raise ValueError("BOT_TOKEN must be configured for the bot")
    token = settings.bot_token.get_secret_value()
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    proxy_url = (
        settings.proxy_url.get_secret_value()
        if settings.proxy_url and settings.proxy_url.get_secret_value()
        else None
    )
    session = AiohttpSession(proxy=proxy_url)
    bot = Bot(token=token, default=default, session=session)

    try:
        setup_dishka(router=dp, container=container)
        cache = await container.get(AiogramCache)
        rate_limit_middleware = AiogramRateLimitMiddleware(
            cache=cache,
            limit=RateLimitConfig(count=5, window_seconds=60, scope="global"),
        )
        dp.message.outer_middleware(rate_limit_middleware)
        dp.callback_query.outer_middleware(rate_limit_middleware)

        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Бот остановлен!")
    finally:
        await session.close()
        await container.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        print("Бот остановлен!")


if __name__ == "__main__":
    main()

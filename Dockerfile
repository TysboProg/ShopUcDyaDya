# -----------------------------------------------------------------------------
# 1. Стадия сборки (Builder): установка зависимостей
# -----------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Отключаем компиляцию в bytecode на этапе сборки и включаем копирование бинарников uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Сначала копируем только файлы зависимостей для эффективного кэширования слоев Docker
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Копируем исходный код проекта
COPY . /app

# Устанавливаем сам проект без dev-зависимостей
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# -----------------------------------------------------------------------------
# 2. Финальная стадия (Runtime): минимальный и безопасный образ
# -----------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

# Создаем не-root пользователя для безопасности
RUN addgroup --system appgroup && adduser --system --group appuser

# Копируем виртуальное окружение (.venv) и код из стадии builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app /app

# Добавляем .venv/bin в PATH, чтобы не писать `/app/.venv/bin/uvicorn`
ENV PATH="/app/.venv/bin:$PATH"

# Переключаемся на безопасного пользователя
USER appuser

EXPOSE 8000

# Запуск сервера Uvicorn
CMD ["uvicorn", "shopucdyadya.app.factory:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
.PHONY: check format typecheck dev bot test worker docker

# --- ПРОВЕРКА КОДА И ИСПРАВЛЕНИЕ КОДА (LINT & FORMAT CHECK & FIX) ---
check:
	uv run ruff check --fix .

# --- ФОРМАТИРОВАНИЕ КОДА (FORMAT) ---
format:
	uv run ruff format .

# --- ПРОВЕРКА ТИПОВ (TYPECHECK) ---
typecheck:
	uv run mypy .

# --- ЗАПУСК WEB-СЕРВЕРА ---
dev:
	uv run uvicorn shopucdyadya.app.factory:create_app --factory --reload

# --- ЗАПУСК БОТА ---
bot:
	uv run python -m shopucdyadya.app.bot

# --- ЗАПУСК ТЕСТОВ ---
test:
	pytest -s -v

# --- ЗАПУСК ВОРКЕРА ДЛЯ ОЧЕРЕДИ ЗАДАЧ ---
worker:
	uv run pgq run shopucdyadya.jobs.worker:main

# --- ЗАПУСК И СБОРКА DOCKER ОБРАЗОВ ---
docker:
	docker compose up -d --build

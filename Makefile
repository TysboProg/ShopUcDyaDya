.PHONY: check format typecheck dev

# --- ПРОВЕРКА КОДА (LINT & FORMAT CHECK) ---
check:
	@echo "---> Checking Python"
	uv run ruff check .

# --- ИСПРАВЛЕНИЕ И ФОРМАТИРОВАНИЕ (FIX & FORMAT) ---
format:
	@echo "---> Formatting Python (Ruff)..."
	uv run ruff format .
	uv run ruff check --fix .

# --- ПРОВЕРКА ТИПОВ (TYPECHECK) ---
# Запускает mypy для Python
typecheck:
	@echo "---> Typechecking Python (mypy)..."
	uv run mypy .

# --- ЗАПУСК И СБОРКА ПРОЕКТА ---
dev:
	uv run uvicorn shopucdyadya.main:app --reload

test:
	pytest -s -v

worker:
	uv run taskiq worker shopucdyadya.workers.broker:broker
	
scheduler:
	uv run taskiq scheduler shopucdyadya.workers.scheduler:scheduler

docker:
	docker compose up -d --build

DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
APP_CONTAINER = app

help:
	@echo "Available commands:"
	@echo "make up        - Start containers"
	@echo "make down      - Stop and delete containers"
	@echo "make app-shell - Opens the terminal of the app container"
	@echo "make logs-all  - Tracking logs of all containers"
	@echo "make test      - Running tests in the app container "
	@echo "make ps        - Viewing container statuses "
	@echo "make config    - Validation of the docker-compose file"

up:
	@echo "$(GREEN)Starting containers...$(NC)"
	${DC} up --build -d

down:
	@echo "$(GREEN)Stopping containers...$(NC)"
	${DC} down

app-shell:
	${EXEC} ${APP_CONTAINER} bash

logs-all:
	${DC} logs -f

test:
	${EXEC} ${APP_CONTAINER} pytest

ps:
	${DC} ps

config:
	${DC} config

.PHONY: help up down app-shell logs-all test ps config
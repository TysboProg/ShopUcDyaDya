FROM python:3.11.9-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip wheel poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY app /app/
COPY migrations /app/migrations/
COPY /scripts/migrate.sh /app/
COPY alembic.ini /app/

RUN chmod +x migrate.sh

ENTRYPOINT ["./migrate.sh"]

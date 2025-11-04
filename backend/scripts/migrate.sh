#!/usr/bin/env bash

set -e

MIGRATIONS_DIR="migrations/versions"

echo "Checking for existing migrations..."

if [ ! -d "$MIGRATIONS_DIR" ] || [ -z "$(find "$MIGRATIONS_DIR" -maxdepth 1 -name '*.py' -print -quit)" ]; then
    echo "No existing migrations found. Creating initial migration..."

    echo "Creating Tables..."
    alembic revision --autogenerate -m "Create Tables"
    echo "Tables migration created!"

    echo "Applying migrations..."
    alembic upgrade head
    echo "Initial migrations applied!"
else
    echo "Existing migrations found. Applying migrations..."
    alembic upgrade head
    echo "Migrations applied!"
fi

exec "$@"
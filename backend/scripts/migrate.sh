#!/usr/bin/env bash

set -e

echo "Create Table"
alembic revision --autogenerate -m "Create Tables"
echo "Table Created"

echo "Run apply migrations.."
alembic upgrade head
echo "Migrations applied!"

exec "$@"
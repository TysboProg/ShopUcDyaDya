#!/bin/sh
set -eu

: "${RUNTIME_DB_USER:?RUNTIME_DB_USER is required}"
: "${RUNTIME_DB_PASSWORD:?RUNTIME_DB_PASSWORD is required}"
: "${MIGRATION_DB_USER:?MIGRATION_DB_USER is required}"
: "${MIGRATION_DB_PASSWORD:?MIGRATION_DB_PASSWORD is required}"

psql \
  --set=ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=app_database="$POSTGRES_DB" \
  --set=runtime_user="$RUNTIME_DB_USER" \
  --set=runtime_password="$RUNTIME_DB_PASSWORD" \
  --set=migration_user="$MIGRATION_DB_USER" \
  --set=migration_password="$MIGRATION_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'runtime_user', :'runtime_password') \gexec
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'migration_user', :'migration_password') \gexec
ALTER DATABASE :"app_database" OWNER TO :"migration_user";
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
ALTER SCHEMA public OWNER TO :"migration_user";
GRANT CONNECT ON DATABASE :"app_database" TO :"runtime_user";
GRANT CONNECT ON DATABASE :"app_database" TO :"migration_user";
GRANT USAGE ON SCHEMA public TO :"runtime_user";
SQL

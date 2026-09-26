import asyncio
import os
import subprocess

import psycache
import psycopg
from psycopg import sql

from shopucdyadya.app.config import settings


def _psycopg_dsn() -> str:
    return (
        settings.require_migration_db_url()
        .unicode_string()
        .replace("postgresql+psycopg://", "postgresql://", 1)
    )


async def _wait_for_postgres(
    dsn: str,
    *,
    attempts: int = 30,
    delay: float = 2.0,
) -> None:
    """Wait until PostgreSQL accepts connections.

    ``depends_on: service_healthy`` protects the normal Compose startup, but
    this retry is still useful after a database restart or a slow volume mount.
    """
    last_error: psycopg.OperationalError | None = None

    for _ in range(attempts):
        try:
            connection = await psycopg.AsyncConnection.connect(dsn)
        except psycopg.OperationalError as error:
            if error.sqlstate is not None:
                raise RuntimeError(
                    "PostgreSQL rejected the db-init connection "
                    f"(SQLSTATE {error.sqlstate}); check the migration role and password"
                ) from error
            last_error = error
            await asyncio.sleep(delay)
        else:
            await connection.close()
            return

    raise RuntimeError("PostgreSQL did not become ready in time") from last_error


async def _pgq_is_installed(dsn: str) -> bool:
    """Return whether the core PgQueuer table and enum already exist."""
    connection = await psycopg.AsyncConnection.connect(dsn)
    try:
        cursor = await connection.execute(
            """
            SELECT to_regclass('public.pgqueuer') IS NOT NULL
               AND to_regtype('public.pgqueuer_status') IS NOT NULL
            """
        )
        row = await cursor.fetchone()
        return bool(row and row[0])
    finally:
        await connection.close()


async def _prepare_database(dsn: str) -> bool:
    await _wait_for_postgres(dsn)
    return await _pgq_is_installed(dsn)


def _run_pgq_install(dsn: str) -> None:
    """Install PgQueuer using PGDSN instead of exposing credentials in argv."""
    environment = os.environ.copy()
    environment["PGDSN"] = dsn

    try:
        # Do not capture output: pgq's stderr is the useful diagnostic in
        # docker compose logs when installation fails.
        subprocess.run(["pgq", "install"], check=True, env=environment)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"PgQueuer installation failed with exit code {error.returncode}"
        ) from error


def _run_alembic_upgrade() -> None:
    """Apply application schema migrations after PgQueuer is available."""
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Alembic migration failed with exit code {error.returncode}") from error


def _grant_runtime_access(dsn: str, runtime_user: str) -> None:
    """Grant the runtime role access to current and future application objects."""
    role = sql.Identifier(runtime_user)
    with psycopg.connect(dsn, autocommit=True) as connection:
        database_name = connection.info.dbname
        if database_name is None:
            raise RuntimeError("Migration database connection has no database name")
        connection.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(database_name), role
            )
        )
        connection.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(role))
        connection.execute(
            sql.SQL(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {}"
            ).format(role)
        )
        connection.execute(
            sql.SQL("GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO {}").format(
                role
            )
        )
        connection.execute(
            sql.SQL("GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO {}").format(role)
        )
        connection.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
                "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {}"
            ).format(role)
        )
        connection.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
                "GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {}"
            ).format(role)
        )
        connection.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO {}"
            ).format(role)
        )

        types = connection.execute(
            """
            SELECT namespace.nspname, type.typname
            FROM pg_type AS type
            JOIN pg_namespace AS namespace ON namespace.oid = type.typnamespace
            WHERE namespace.nspname = 'public'
              AND type.typtype IN ('e', 'd', 'c')
            """
        ).fetchall()
        for schema_name, type_name in types:
            connection.execute(
                sql.SQL("GRANT USAGE ON TYPE {}.{} TO {}").format(
                    sql.Identifier(schema_name),
                    sql.Identifier(type_name),
                    role,
                )
            )


def _install_psycache(dsn: str) -> None:
    """Create psycache's external table before starting restricted runtime roles."""
    with psycopg.connect(dsn, autocommit=True) as connection:
        psycache.init_db(connection)


def main() -> None:
    dsn = _psycopg_dsn()
    if asyncio.run(_prepare_database(dsn)):
        print("PgQueuer is already installed; skipping initialization")
    else:
        _run_pgq_install(dsn)

    _run_alembic_upgrade()
    _install_psycache(dsn)
    runtime_user = os.environ.get("RUNTIME_DB_USER")
    if not runtime_user:
        raise RuntimeError("RUNTIME_DB_USER must be configured for db-init")
    _grant_runtime_access(dsn, runtime_user)


if __name__ == "__main__":
    main()

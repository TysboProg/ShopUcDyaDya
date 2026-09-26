import asyncio
import sys
from logging.config import fileConfig
from typing import TYPE_CHECKING

from alembic import context
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.schema import (
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    SchemaItem,
    Table,
    UniqueConstraint,
)

from shopucdyadya.app.config import settings
from shopucdyadya.infra.base_model import Base
from shopucdyadya.modules import models as _models  # noqa: F401

if TYPE_CHECKING:
    from alembic.environment import IncludeObjectFn, NameFilterType

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

if not config.get_main_option("sqlalchemy.url"):
    database_url = settings.migration_db_url or settings.runtime_db_url
    if database_url is None:
        raise RuntimeError("MIGRATION_DB_URL or RUNTIME_DB_URL must be configured for Alembic")
    config.set_main_option("sqlalchemy.url", database_url.encoded_string())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(
    object: SchemaItem,
    name: str | None,
    type_: "NameFilterType",
    reflected: bool,
    compare_to: SchemaItem | None,
) -> bool:
    ignored_tables = ("pgqueuer", "psycache", "rate_limits", "shopucdyadya_cache_cache_store")
    ignored_prefixes = ("pgqueuer_",)

    if (
        type_ == "table"
        and name is not None
        and (name.startswith(ignored_prefixes) or name in ignored_tables)
    ):
        return False

    if isinstance(object, (Index, UniqueConstraint, ForeignKeyConstraint, CheckConstraint)):
        parent_table = object.table
        if isinstance(parent_table, Table):
            t_name = parent_table.name
            if (
                t_name is not None
                and t_name.startswith(ignored_prefixes)
                or t_name in ignored_tables
            ):
                return False

    return True


if TYPE_CHECKING:
    _assert_type: "IncludeObjectFn" = include_object


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    section = config.get_section(config.config_ini_section)
    if section is None:
        raise RuntimeError("Alembic config section is missing")

    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    loop_factory = None
    if sys.platform == "win32":
        loop_factory = asyncio.SelectorEventLoop

    asyncio.run(run_async_migrations(), loop_factory=loop_factory)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

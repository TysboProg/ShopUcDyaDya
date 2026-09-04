import pytest
from sqlalchemy import inspect, text

@pytest.mark.asyncio
async def test_database(db_session) -> None:
    """Test that the database connection works."""
    result = await db_session.execute(text("SELECT current_database()"))
    value = result.scalar()
    assert value == "shopucdyadya"


@pytest.mark.asyncio
async def test_list_tables_with_columns(async_engine) -> None:
    def get_tables(sync_conn):
        inspector = inspect(sync_conn)
        return inspector.get_table_names()

    # Запускаем синхронную инспекцию через run_sync
    async with async_engine.connect() as conn:
        table_names = await conn.run_sync(get_tables)

    assert len(table_names) > 0, "В базе данных нет ни одной таблицы — миграции не применились?"

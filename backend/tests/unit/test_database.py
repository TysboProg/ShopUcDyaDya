import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database(db_session):
    """Test that the database connection works."""
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()
    assert value == 1

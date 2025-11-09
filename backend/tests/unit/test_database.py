import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database(db_session):
    """Test that the database connection works."""
    result = await db_session.execute(text("SELECT current_database()"))
    value = result.scalar()
    assert value == "tests"

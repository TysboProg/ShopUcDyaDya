"""initial

Revision ID: 6280c1831b8b
Revises:
Create Date: 2026-09-26 14:10:45.868583

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6280c1831b8b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNLOGGED TABLE IF NOT EXISTS rate_limits (
            key           TEXT PRIMARY KEY,
            window_start  BIGINT NOT NULL,
            count         INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_rate_limits_window
            ON rate_limits (window_start);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS rate_limits")

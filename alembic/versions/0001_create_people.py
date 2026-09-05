"""Create the people table.

Revision ID: 0001_create_people
Revises:
Create Date: 2026-09-05
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001_create_people"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            occupation TEXT NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE people")
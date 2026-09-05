"""Create the shortlist table.

Revision ID: 0002_create_shortlist
Revises: 0001_create_people
Create Date: 2026-09-05
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_create_shortlist"
down_revision: str | None = "0001_create_people"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS shortlist (
            people_id TEXT NOT NULL,
            favorite BOOLEAN NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE shortlist")

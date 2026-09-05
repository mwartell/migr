"""Seed a shortlist row for every person.

Revision ID: 0004_seed_shortlist
Revises: 0003_seed_people
Create Date: 2026-09-05
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004_seed_shortlist"
down_revision: str | None = "0003_seed_people"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO shortlist (people_id, favorite)
        SELECT
            id,
            row_number() OVER (ORDER BY id) <= (
                SELECT count(*) / 5 FROM people
            )
        FROM people
    """)


def downgrade() -> None:
    op.execute("DELETE FROM shortlist")

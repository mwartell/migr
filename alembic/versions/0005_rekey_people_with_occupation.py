"""Rekey people IDs to include occupation.

Revision ID: 0005_rekey_people_with_occupation
Revises: 0004_seed_shortlist
Create Date: 2026-09-05
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0005_rekey_people_occupation"
down_revision: str | None = "0004_seed_shortlist"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("ALTER TABLE people ADD COLUMN new_id TEXT")
    op.execute("""
        UPDATE people
        SET new_id = left(
            encode(
                digest(first_name || ':' || last_name || ':' || occupation, 'sha256'),
                'hex'
            ),
            8
        )
    """)
    op.execute("""
        UPDATE shortlist AS candidate
        SET people_id = person.new_id
        FROM people AS person
        WHERE candidate.people_id = person.id
    """)
    op.execute("ALTER TABLE people ALTER COLUMN new_id SET NOT NULL")
    op.execute("ALTER TABLE people DROP COLUMN id")
    op.execute("ALTER TABLE people RENAME COLUMN new_id TO id")
    op.execute("ALTER TABLE people ADD CONSTRAINT people_pkey PRIMARY KEY (id)")
    op.execute("""
        ALTER TABLE shortlist
        ADD CONSTRAINT shortlist_people_id_fkey
        FOREIGN KEY (people_id) REFERENCES people (id)
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE shortlist DROP CONSTRAINT shortlist_people_id_fkey")
    op.execute("ALTER TABLE people DROP CONSTRAINT people_pkey")
    op.execute("ALTER TABLE people ADD COLUMN old_id TEXT")
    op.execute("""
        UPDATE people
        SET old_id = left(
            encode(
                digest(first_name || ':' || last_name, 'sha256'),
                'hex'
            ),
            8
        )
    """)
    op.execute("""
        UPDATE shortlist AS candidate
        SET people_id = person.old_id
        FROM people AS person
        WHERE candidate.people_id = person.id
    """)
    op.execute("ALTER TABLE people ALTER COLUMN old_id SET NOT NULL")
    op.execute("ALTER TABLE people DROP COLUMN id")
    op.execute("ALTER TABLE people RENAME COLUMN old_id TO id")

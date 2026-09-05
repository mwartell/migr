"""Seed sample people.

Revision ID: 0003_seed_people
Revises: 0002_create_shortlist
Create Date: 2026-09-05
"""

from collections.abc import Sequence
from hashlib import sha256

import sqlalchemy as sa

from alembic import op

revision: str = "0003_seed_people"
down_revision: str | None = "0002_create_shortlist"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

people = sa.table(
    "people",
    sa.column("id", sa.Text),
    sa.column("first_name", sa.Text),
    sa.column("last_name", sa.Text),
    sa.column("occupation", sa.Text),
)

sample_people = [
    ("Ada", "Bennett", "Software Engineer"),
    ("Marcus", "Chen", "Architect"),
    ("Priya", "Desai", "Data Analyst"),
    ("Elena", "Foster", "Teacher"),
    ("Jonah", "Garcia", "Electrician"),
]


def person_id(first_name: str, last_name: str) -> str:
    return sha256(f"{first_name}:{last_name}".encode()).hexdigest()[:8]


def upgrade() -> None:
    op.bulk_insert(
        people,
        [
            {
                "id": person_id(first_name, last_name),
                "first_name": first_name,
                "last_name": last_name,
                "occupation": occupation,
            }
            for first_name, last_name, occupation in sample_people
        ],
    )


def downgrade() -> None:
    op.execute(
        people.delete().where(
            people.c.id.in_(
                [
                    person_id(first_name, last_name)
                    for first_name, last_name, _ in sample_people
                ]
            )
        )
    )

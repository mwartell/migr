"""Manage a connection to the migr postgres database."""

from contextlib import contextmanager
from typing import Any, Self

import psycopg
from psycopg.rows import dict_row

DEFAULT_DSN = "dbname=migr"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS people (
    id         SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    occupation TEXT NOT NULL
)
"""


class Database:
    """A context-managed connection to the migr database."""

    def __init__(self, dsn: str = DEFAULT_DSN, autocommit: bool = True) -> None:
        self._conn = psycopg.connect(dsn, autocommit=autocommit, row_factory=dict_row)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    def create_people_table(self) -> None:
        """Create the people (id, first_name, last_name, occupation) table."""
        with self._conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)

    @contextmanager
    def cursor(self):
        """Yield a cursor returning rows as dicts."""
        with self._conn.cursor() as cur:
            yield cur

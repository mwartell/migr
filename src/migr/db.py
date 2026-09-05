"""Manage a connection to the migr postgres database."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Self

import psycopg
from alembic.config import Config
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
from sqlalchemy import URL

from alembic import command
from migr import PROJECT_ROOT

DEFAULT_DSN = "dbname=migr"
ALEMBIC_DIR = PROJECT_ROOT / "alembic"


def migrate(dsn: str = DEFAULT_DSN, revision: str = "head") -> None:
    """Apply migrations through the requested Alembic revision."""
    info = conninfo_to_dict(dsn)
    connection_keys = {"dbname", "host", "password", "port", "user"}
    username = info.get("user")
    password = info.get("password")
    host = info.get("host")
    port = info.get("port")
    database = info.get("dbname")
    url = URL.create(
        "postgresql+psycopg",
        username=username if isinstance(username, str) else None,
        password=password if isinstance(password, str) else None,
        host=host if isinstance(host, str) else None,
        port=int(port) if isinstance(port, str | int) else None,
        database=database if isinstance(database, str) else None,
        query={
            key: str(value)
            for key, value in info.items()
            if key not in connection_keys and value is not None
        },
    )
    config = Config()
    config.set_main_option("script_location", str(ALEMBIC_DIR))
    config.set_main_option("sqlalchemy.url", url.render_as_string(hide_password=False))
    command.upgrade(config, revision)


class Database:
    """A context-managed connection to the migr database."""

    def __init__(self, dsn: str = DEFAULT_DSN, autocommit: bool = True) -> None:
        self._conn = psycopg.Connection[dict[str, Any]].connect(
            dsn, autocommit=autocommit, row_factory=dict_row
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_dummy: object) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    def people_with_shortlist(self) -> list[dict[str, Any]]:
        """Return people with their manually joined shortlist status."""
        with self.cursor() as cur:
            cur.execute("""
                SELECT
                    people.id,
                    people.first_name,
                    people.last_name,
                    people.occupation,
                    shortlist.favorite
                FROM people
                LEFT JOIN shortlist ON shortlist.people_id = people.id
                ORDER BY people.last_name, people.first_name
            """)
            return cur.fetchall()

    @contextmanager
    def cursor(self) -> Generator[psycopg.Cursor[dict[str, Any]]]:
        """Yield a cursor returning rows as dicts."""
        with self._conn.cursor() as cur:
            yield cur

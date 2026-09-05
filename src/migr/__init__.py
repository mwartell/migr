from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

from rich.console import Console
from rich.table import Table

from migr.db import Database, migrate


def main() -> None:
    migrate(revision="0002_create_shortlist")
    with Database() as database:
        people = database.people_with_shortlist()

    table = Table("ID", "First name", "Last name", "Occupation", "Favorite")
    for person in people:
        table.add_row(
            str(person["id"]),
            str(person["first_name"]),
            str(person["last_name"]),
            str(person["occupation"]),
            str(person["favorite"]),
        )
    Console().print(table)

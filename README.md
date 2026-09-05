⁅※ written by a human for humans ※⁆

# table rekeying with alembic migrations

Begin with `uv sync` in the project root and activate the .venv in your favorite way. This will get you the `alembic` migration cli and the `migr` tool which dumps the current database.

Running the demo requires a running local postgres with null credentials

      brew install postgresql
      brew services start postgresql@18

Then create the `migr` database used by the demo

      createdb migr


We'll use a simple schema to model the problem we have in Shine:

      people = (id, first, last, occupation)
      shortlist = (people_id, favorite)

The database is currently empty and running the local `migr` script shows that

      > migr
      ┏━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
      ┃ ID ┃ First name ┃ Last name ┃ Occupation ┃ Favorite ┃
      ┡━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
      └────┴────────────┴───────────┴────────────┴──────────┘

For demo simplicity, the `migr` dump cli actually runs the first two migrations so the tables exist. There are five migrations in the alembic/versions directory

      0001_create_people.py
      0002_create_shortlist.py
      0003_seed_people.py
      0004_seed_shortlist.py
      0005_rekey_people_with_occupation.py

with the obvious functions. The create migrations create the two simple tables, and the seed migrations fill them. Alembic is used to execute the migrations and it provides an upgrade command:

      alembic upgrade 0004

says to run all migrations up through `0004_seed_shortlist`. This seeds the tables which we can dump

      > migr
      ┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
      ┃ ID       ┃ First name ┃ Last name ┃ Occupation        ┃ Favorite ┃
      ┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
      │ 16f27277 │ Ada        │ Bennett   │ Software Engineer │ True     │
      │ 78539aa2 │ Marcus     │ Chen      │ Architect         │ False    │
      │ 33627df2 │ Priya      │ Desai     │ Data Analyst      │ False    │
      │ 8dfc05e8 │ Elena      │ Foster    │ Teacher           │ False    │
      │ 35577812 │ Jonah      │ Garcia    │ Electrician       │ False    │
      └──────────┴────────────┴───────────┴───────────────────┴──────────┘

The 0003 people seeder makes the ID from a hash of the first and last names. This is the "old" key analog that we need to patch up in Shine.

Migration 0005 is the core of this demo. It computes the new key which is a hash of `first:last:occupation` that will be different than the old key. This is put in a `new_key` column of the people table The problem is that the shortlist table is keyed by the old key so the migration uses the new and old keys in the `people` table to re-key `shortlist`.

Finally, the 0005 migration renames the new_key column to `id`. While we're at it, we add proper key constraints so that a shortlist people_id must match a primary key in the people table. Running `alembic upgrade 0005` rekeys both tables

      > migr
      ┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
      ┃ ID       ┃ First name ┃ Last name ┃ Occupation        ┃ Favorite ┃
      ┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
      │ 740d785b │ Ada        │ Bennett   │ Software Engineer │ True     │
      │ 8814f2f4 │ Marcus     │ Chen      │ Architect         │ False    │
      │ a52454a1 │ Priya      │ Desai     │ Data Analyst      │ False    │
      │ 7c26c28f │ Elena      │ Foster    │ Teacher           │ False    │
      │ 4e08960c │ Jonah      │ Garcia    │ Electrician       │ False    │
      └──────────┴────────────┴───────────┴───────────────────┴──────────┘


# Structured migrations using [Alembic](https://github.com/sqlalchemy/alembic)

The migrations and seeding in the current Shine db modules is clunky. Through a combination of shell scripts, sql definitions and a Justfile, we've got a homebrew and error-prone migration method.

Alembic, which I wasn't familiar with prior to looking at this problem, is made by the SqlAlchemy folks and appears to be the frontrunner migration tool in the Python realm. It records the state of migrations in the database itself. The key features are upgrade and downgrade of migration. For example, if you didn't like the result of the 0005 migration above you could `alembic downgrade 0004` and rollback the new key mapping. Alembic also preserves transactional integrity, so either the whole migration works or none of it does.

Alembic encourages, and makes it easy to keep all database modifications structured. As an example, we've had to play around with seed data far more than we'd like. Similar to Infrastructure as Code, Alembic prefers database-structure as code where you can always replay it and let the system avoid creating duplicate rows.

Alembic installs with `uv add` and brings surprisingly few dependencies. It is actively maintained and appears feature complete.

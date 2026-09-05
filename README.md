# Rekeying Hash-Based IDs

At revision `0004_seed_shortlist`, this project models a person whose `id` is
derived from `first_name` and `last_name`:

```python
sha256(f"{first_name}:{last_name}".encode()).hexdigest()[:8]
```

`people.occupation` is currently not part of that identity. The `shortlist`
table holds a textual `people_id` value rather than a database foreign key.
This is the equivalent of the production situation where another table stores
the old person ID as text: PostgreSQL cannot automatically cascade an ID
change because it has no declared relationship to follow.

The revised ID must include occupation:

```text
sha256(first_name + ":" + last_name + ":" + occupation)[:8]
```

Changing this formula invalidates every old ID, including the values in
`shortlist.people_id`. Updating `people.id` first would discard the only join
key that can connect each textual reference to its replacement.

## Migration strategy

Revision `0005_rekey_people_occupation` performs the rekey entirely in
PostgreSQL, in one Alembic migration transaction:

1. It adds `people.new_id` as a temporary text column and uses
   `pgcrypto.digest(..., 'sha256')` to calculate the new key from the three
   identity fields. `encode(..., 'hex')` and `left(..., 8)` match the existing
   Python hash representation.
2. While each row has both identifiers, it updates the textual references with
   `UPDATE shortlist ... FROM people` by joining
   `shortlist.people_id = people.id` and assigning `people.new_id`.
3. It marks the calculated temporary column `NOT NULL`, drops the old `id`, and
   renames `new_id` to `id`.

The ordering is the essential part: the old and new keys coexist only long
enough to rekey every dependent textual reference. The downgrade repeats the
same process in reverse, calculating the original name-only hash in `old_id`
before switching the columns back.

The sample uses eight hexadecimal characters to match the existing model. A
real system should use a sufficiently long digest and enforce uniqueness before
relying on a hash as an identifier; truncated hashes can collide. If the
production hash is implemented outside PostgreSQL, expose an equivalent SQL
function (or preserve an explicit old-to-new mapping table) so the same
set-based migration remains possible.

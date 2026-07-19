"""unique_category_name

Revision ID: f1a2b3c4d5e6
Revises: e7f8a9b0c1d2
Create Date: 2026-07-15 14:00:00.000000

A nomenklatura (category) is now a unique year number (e.g. "2024") — no
duplicates allowed. Adds a UNIQUE constraint on ``categories.name``.

Before adding the constraint, any pre-existing duplicate names are made unique
by appending a numeric suffix (legacy rows only; going forward the API enforces
a 4-digit year and rejects duplicates).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e7f8a9b0c1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Deduplicate existing names so the unique constraint can be added on any
    # data set. Dialect-agnostic (runs through the active connection).
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id, name FROM categories ORDER BY created_at")
    ).fetchall()
    seen: dict[str, int] = {}
    for row_id, name in rows:
        if name in seen:
            seen[name] += 1
            new_name = f"{name} ({seen[name]})"
            conn.execute(
                sa.text("UPDATE categories SET name = :n WHERE id = :i"),
                {"n": new_name, "i": row_id},
            )
        else:
            seen[name] = 1

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_categories_name', ['name'])


def downgrade() -> None:
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_constraint('uq_categories_name', type_='unique')

"""add_retention_period_reference_table

Revision ID: b7e1f8c3a912
Revises: a3f1c2d4e5b6
Create Date: 2026-05-15 09:00:00.000000

Replaces the previous String(20) `retention_period` enum on archive_folders
with an FK to a new `retention_periods` reference table:

  - creates `retention_periods` (id UUID, name, created_at)
  - seeds it from data/Saqlash muddati.json (explicit UUIDs preserved)
  - adds `retention_period_id` UUID FK on archive_folders
  - maps every legacy enum string to the closest seeded UUID (anything
    that has no clean match falls back to "-")
  - drops the old `retention_period` column

The legacy → UUID map only covers the StrEnum values that were ever stored:
3_years / 5_years / 10_years / 25_years / 50_years / 75_years / permanent / epk.
"""
import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b7e1f8c3a912'
down_revision: Union[str, None] = 'a3f1c2d4e5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RETENTION_FILE = "Saqlash muddati.json"

# Sentinel UUIDs the legacy migration falls back on when nothing in the new
# reference list matches the old enum value.
DASH_UUID = "a77ed3cd-1277-4a67-914c-5782ab6cc296"          # "-"

# Map StrEnum value -> retention_periods.id (from data/Saqlash muddati.json).
LEGACY_TO_NEW: dict[str, str] = {
    "3_years":   "997b326b-d093-47dc-997c-f59c4936ca66",   # 3 yil
    "5_years":   "dace00b4-ede7-428c-b9ac-5c08fd040790",   # 5 yil
    "10_years":  "08f2b89f-7d3a-41d3-9b2f-53438d08653e",   # 10 yil
    "25_years":  DASH_UUID,                                  # no exact match
    "50_years":  "6aee95d9-5162-480d-986e-4196f051d1d3",   # 50 yil
    "75_years":  "d38846f0-bce4-4ce2-8603-6969a82d36ad",   # 75 yil
    "permanent": "67d60166-2e51-41d9-86fc-b89690c69892",   # Doimiy
    "epk":       DASH_UUID,                                  # no exact match
}


def _load_seed_rows() -> list[dict]:
    path = DATA_DIR / RETENTION_FILE
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict] = []
    seen: set[str] = set()
    for entry in data if isinstance(data, list) else []:
        rid = (entry or {}).get("id")
        name = ((entry or {}).get("name") or "").strip()
        if not rid or not name or str(rid) in seen:
            continue
        seen.add(str(rid))
        rows.append({"id": str(rid), "name": name})
    return rows


def upgrade() -> None:
    op.create_table(
        'retention_periods',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    seed_rows = _load_seed_rows()
    if seed_rows:
        table = sa.table(
            'retention_periods',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
        )
        op.bulk_insert(table, seed_rows)

    # 1) Add the new FK column (nullable so the migration can populate it).
    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('retention_period_id', sa.String(length=36), nullable=True))

    # 2) Backfill: map legacy enum strings to the new UUIDs.
    bind = op.get_bind()
    seed_ids = {row['id'] for row in seed_rows}
    if seed_ids:
        for legacy, new_id in LEGACY_TO_NEW.items():
            if new_id not in seed_ids:
                # Skip if the JSON seed didn't include the target UUID — leaving
                # the FK NULL is preferable to a dangling reference.
                continue
            bind.execute(
                sa.text(
                    "UPDATE archive_folders SET retention_period_id = :new_id "
                    "WHERE retention_period = :legacy"
                ),
                {"new_id": new_id, "legacy": legacy},
            )

    # 3) Wire up the FK constraint and drop the legacy column.
    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_archive_folders_retention_period_id',
            'retention_periods', ['retention_period_id'], ['id'],
            ondelete='SET NULL',
        )
        batch_op.drop_column('retention_period')


def downgrade() -> None:
    # Re-add the legacy column as nullable (we cannot reliably reconstruct the
    # original enum values), then drop the FK + reference table.
    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('retention_period', sa.String(length=20), nullable=True))
        batch_op.drop_constraint('fk_archive_folders_retention_period_id', type_='foreignkey')
        batch_op.drop_column('retention_period_id')
    op.drop_table('retention_periods')

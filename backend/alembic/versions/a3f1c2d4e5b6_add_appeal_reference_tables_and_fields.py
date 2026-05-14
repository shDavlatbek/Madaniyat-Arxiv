"""add_appeal_reference_tables_and_fields

Revision ID: a3f1c2d4e5b6
Revises: d8f3a2c1e9b4
Create Date: 2026-05-14 23:10:00.000000

Adds the reference tables backing the Murojaat (appeal) document form:
- `regions`           — seeded from data/region-local.json + data/region-abroad.json
- `reception_places`  — seeded from data/Qabul qilingan joy.json
- `appeal_types`      — seeded from data/Murojaat turi.json

…and the appeal-specific columns on `documents`:
- region_id, country_id      -> regions.id      (ON DELETE SET NULL)
- reception_place_id         -> reception_places.id (ON DELETE SET NULL)
- appeal_type_id             -> appeal_types.id (ON DELETE SET NULL)
- person_type, outgoing_number, outgoing_date, signed_by, note

Seeding preserves the explicit UUIDs from the JSON files and is skipped
gracefully if a file is absent so `alembic upgrade head` always succeeds.
"""
import json
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f1c2d4e5b6'
down_revision: Union[str, None] = 'd8f3a2c1e9b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _load(filename: str) -> list:
    path = DATA_DIR / filename
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _seed_id_name(table_name: str, columns: list[str], rows: list[dict]) -> None:
    if not rows:
        return
    table = sa.table(table_name, *[sa.column(c, sa.String) for c in columns])
    op.bulk_insert(table, rows)


def upgrade() -> None:
    op.create_table(
        'regions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'reception_places',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'appeal_types',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('region_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('country_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('reception_place_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('appeal_type_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('person_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('outgoing_number', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('outgoing_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('signed_by', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('note', sa.Text(), nullable=True))
        batch_op.create_foreign_key(
            'fk_documents_region_id', 'regions', ['region_id'], ['id'], ondelete='SET NULL',
        )
        batch_op.create_foreign_key(
            'fk_documents_country_id', 'regions', ['country_id'], ['id'], ondelete='SET NULL',
        )
        batch_op.create_foreign_key(
            'fk_documents_reception_place_id', 'reception_places', ['reception_place_id'], ['id'], ondelete='SET NULL',
        )
        batch_op.create_foreign_key(
            'fk_documents_appeal_type_id', 'appeal_types', ['appeal_type_id'], ['id'], ondelete='SET NULL',
        )

    # --- Seed reference data (preserve explicit UUIDs; skip dupes/invalid) ---
    region_rows: list[dict] = []
    seen_regions: set[str] = set()
    for filename, default_type in (("region-local.json", "LOCAL"), ("region-abroad.json", "ABROAD")):
        for entry in _load(filename):
            rid = (entry or {}).get("id")
            name = ((entry or {}).get("name") or "").strip()
            rtype = ((entry or {}).get("type") or default_type).strip().upper()
            if not rid or not name or str(rid) in seen_regions:
                continue
            seen_regions.add(str(rid))
            region_rows.append({"id": str(rid), "name": name, "type": rtype})
    _seed_id_name('regions', ['id', 'name', 'type'], region_rows)

    def _id_name_rows(entries: list) -> list[dict]:
        rows, seen = [], set()
        for entry in entries:
            rid = (entry or {}).get("id")
            name = ((entry or {}).get("name") or "").strip()
            if not rid or not name or str(rid) in seen:
                continue
            seen.add(str(rid))
            rows.append({"id": str(rid), "name": name})
        return rows

    _seed_id_name('reception_places', ['id', 'name'], _id_name_rows(_load("Qabul qilingan joy.json")))
    _seed_id_name('appeal_types', ['id', 'name'], _id_name_rows(_load("Murojaat turi.json")))


def downgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_constraint('fk_documents_appeal_type_id', type_='foreignkey')
        batch_op.drop_constraint('fk_documents_reception_place_id', type_='foreignkey')
        batch_op.drop_constraint('fk_documents_country_id', type_='foreignkey')
        batch_op.drop_constraint('fk_documents_region_id', type_='foreignkey')
        batch_op.drop_column('note')
        batch_op.drop_column('signed_by')
        batch_op.drop_column('outgoing_date')
        batch_op.drop_column('outgoing_number')
        batch_op.drop_column('person_type')
        batch_op.drop_column('appeal_type_id')
        batch_op.drop_column('reception_place_id')
        batch_op.drop_column('country_id')
        batch_op.drop_column('region_id')
    op.drop_table('appeal_types')
    op.drop_table('reception_places')
    op.drop_table('regions')

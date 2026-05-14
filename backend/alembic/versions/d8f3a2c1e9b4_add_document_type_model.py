"""add_document_type_model

Revision ID: d8f3a2c1e9b4
Revises: c194aedf42a6
Create Date: 2026-05-14 21:30:00.000000

Adds the `document_types` reference taxonomy (Hujjat turi) and links it to
`documents` via a nullable `document_type_id` FK (ON DELETE SET NULL).

The table is seeded from `backend/types.json` (~120 entries), preserving the
explicit UUIDs from that file. Seeding is skipped gracefully if the file is
absent so `alembic upgrade head` always succeeds.
"""
import json
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8f3a2c1e9b4'
down_revision: Union[str, None] = 'c194aedf42a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'document_types',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_type_id', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            'fk_documents_document_type_id',
            'document_types',
            ['document_type_id'],
            ['id'],
            ondelete='SET NULL',
        )

    # Seed from backend/types.json (this file lives at backend/alembic/versions/).
    types_path = Path(__file__).resolve().parents[2] / "types.json"
    if not types_path.exists():
        return
    data = json.loads(types_path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    rows = []
    for entry in data:
        name = (entry.get("name") or "").strip()
        type_id = entry.get("id")
        if not name or not type_id or name in seen:
            continue
        seen.add(name)
        rows.append({"id": str(type_id), "name": name})
    if rows:
        document_types = sa.table(
            'document_types',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
        )
        op.bulk_insert(document_types, rows)


def downgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_constraint('fk_documents_document_type_id', type_='foreignkey')
        batch_op.drop_column('document_type_id')
    op.drop_table('document_types')

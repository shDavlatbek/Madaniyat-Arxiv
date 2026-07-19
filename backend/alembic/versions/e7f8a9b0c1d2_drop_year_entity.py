"""drop_year_entity

Revision ID: e7f8a9b0c1d2
Revises: d5e6f7a8b9c0
Create Date: 2026-07-15 12:00:00.000000

Nomenklatura (Category) becomes the top-level document grouping and the Year
entity is removed entirely. Hard-drops:

  * documents.year_id        (FK -> years.id)
  * categories.year_id       (FK -> years.id)
  * archive_folders.year_id  (FK -> years.id, plus the (year_id, index_code)
                              unique constraint)
  * departments.year_id      (FK -> years.id, added in d5e6f7a8b9c0)
  * the ``years`` table itself

Documents keep their ``category_id`` (their nomenklatura), so no document data
is lost — only the now-redundant year link goes. On PostgreSQL a DROP COLUMN
automatically drops the dependent FK / unique constraint; the SQLite dev path
recreates each table via batch mode.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, None] = 'd5e6f7a8b9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop every year_id column first (this also drops the FK to years and, for
    # archive_folders, the (year_id, index_code) unique constraint) so the
    # years table has no remaining dependants.
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('year_id')

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_column('year_id')

    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.drop_column('year_id')

    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.drop_column('year_id')

    op.drop_table('years')


def downgrade() -> None:
    # Structural rollback only — the years table's rows and the per-row year
    # links cannot be recovered (hard-drop). Recreate the table and nullable
    # columns so the schema shape is restored.
    op.create_table(
        'years',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('value'),
    )

    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('year_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('year_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('year_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('year_id', sa.Integer(), nullable=True))

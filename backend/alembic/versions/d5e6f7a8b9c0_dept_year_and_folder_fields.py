"""dept_year_and_folder_fields

Revision ID: d5e6f7a8b9c0
Revises: 81b4b241c269
Create Date: 2026-07-14 10:00:00.000000

Archive rework (dorabotka):

  * departments.year_id      -> NEW FK departments.year_id -> years.id
                                ("Bo'limga yil qo'shish")
  * archive_folders.list_number  -> NEW "Ro'yxat raqami" (after "Modda raqami")
  * archive_folders.total_sheets -> NEW "Umumiy varaqlar soni" (manual total;
                                the automatic sum of the folder's documents'
                                pages is computed at query time, not stored)

start_date / end_date already exist on archive_folders (legacy, nullable) and
are simply re-surfaced by the redesigned form — no schema change needed.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, None] = '81b4b241c269'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('year_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_departments_year_id',
            'years', ['year_id'], ['id'],
            ondelete='SET NULL',
        )

    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('list_number', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('total_sheets', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.drop_column('total_sheets')
        batch_op.drop_column('list_number')

    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_departments_year_id', type_='foreignkey')
        batch_op.drop_column('year_id')

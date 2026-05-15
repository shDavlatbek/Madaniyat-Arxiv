"""redesign_archive_folder_fields

Revision ID: c8a3d5e2f041
Revises: b7e1f8c3a912
Create Date: 2026-05-15 09:45:00.000000

Switches archive_folders to the 7-field structure agreed with the partner
system:

  Bo'lim nomi          -> archive_folders.department_id (FK departments.id)
  Bo'lim indeksi       -> departments.index_code (NEW column on departments)
  Yig'ma jild indeksi  -> archive_folders.index_code (existing)
  Yig'ma jild sarlavhasi -> archive_folders.title (existing)
  Modda raqami         -> archive_folders.article_number (NEW)
  Saqlash muddati      -> archive_folders.retention_period_id (existing FK)
  Eslatma              -> archive_folders.note (NEW)

Also relaxes archive_folders.start_date to NULLABLE so the field can be
omitted in the new form (existing rows keep their value; end_date and
year_id remain available but are no longer surfaced).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c8a3d5e2f041'
down_revision: Union[str, None] = 'b7e1f8c3a912'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('index_code', sa.String(length=50), nullable=True))

    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('department_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('article_number', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('note', sa.Text(), nullable=True))
        batch_op.alter_column('start_date', existing_type=sa.Date(), existing_nullable=False, nullable=True)
        batch_op.create_foreign_key(
            'fk_archive_folders_department_id',
            'departments', ['department_id'], ['id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    with op.batch_alter_table('archive_folders', schema=None) as batch_op:
        batch_op.drop_constraint('fk_archive_folders_department_id', type_='foreignkey')
        batch_op.alter_column('start_date', existing_type=sa.Date(), existing_nullable=True, nullable=False)
        batch_op.drop_column('note')
        batch_op.drop_column('article_number')
        batch_op.drop_column('department_id')

    with op.batch_alter_table('departments', schema=None) as batch_op:
        batch_op.drop_column('index_code')

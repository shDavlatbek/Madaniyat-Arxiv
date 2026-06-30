"""add_passport_and_school_location

Revision ID: 81b4b241c269
Revises: 9be85ab9e7c6
Create Date: 2026-05-25 11:44:17.691180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81b4b241c269'
down_revision: Union[str, None] = '9be85ab9e7c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add location columns to music_schools
    with op.batch_alter_table('music_schools', schema=None) as batch_op:
        batch_op.add_column(sa.Column('region', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('district', sa.String(length=100), nullable=True))

    # 2. Add passport and pinfl columns to music_school_documents
    with op.batch_alter_table('music_school_documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('passport_series', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('passport_number', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('pinfl', sa.String(length=14), nullable=True))


def downgrade() -> None:
    # 1. Remove columns from music_school_documents
    with op.batch_alter_table('music_school_documents', schema=None) as batch_op:
        batch_op.drop_column('pinfl')
        batch_op.drop_column('passport_number')
        batch_op.drop_column('passport_series')

    # 2. Remove columns from music_schools
    with op.batch_alter_table('music_schools', schema=None) as batch_op:
        batch_op.drop_column('district')
        batch_op.drop_column('region')

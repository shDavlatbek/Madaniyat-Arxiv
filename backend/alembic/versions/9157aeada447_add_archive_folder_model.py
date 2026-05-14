"""add_archive_folder_model

Revision ID: 9157aeada447
Revises: c4997a1212a2
Create Date: 2026-05-14 19:07:00.075080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9157aeada447'
down_revision: Union[str, None] = 'c4997a1212a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'archive_folders',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('index_code', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('retention_period', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('year_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['year_id'], ['years.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year_id', 'index_code'),
    )


def downgrade() -> None:
    op.drop_table('archive_folders')

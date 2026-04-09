"""remove target column from documents

Revision ID: bc460598793c
Revises: e3233e7efaab
Create Date: 2026-04-09 11:49:53.542425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc460598793c'
down_revision: Union[str, None] = 'e3233e7efaab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('target')


def downgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('target', sa.VARCHAR(length=500), nullable=True))

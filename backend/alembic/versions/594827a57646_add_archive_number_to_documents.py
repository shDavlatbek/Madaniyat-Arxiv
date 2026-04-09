"""add_archive_number_to_documents

Revision ID: 594827a57646
Revises: bc460598793c
Create Date: 2026-04-09 18:30:06.332831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '594827a57646'
down_revision: Union[str, None] = 'bc460598793c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('archive_number', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint('uq_documents_archive_number', ['archive_number'])


def downgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_constraint('uq_documents_archive_number', type_='unique')
        batch_op.drop_column('archive_number')

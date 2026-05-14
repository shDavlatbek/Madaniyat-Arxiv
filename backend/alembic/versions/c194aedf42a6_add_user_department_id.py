"""add_user_department_id

Revision ID: c194aedf42a6
Revises: cfad24348323
Create Date: 2026-05-14 20:30:16.371363

Links users to departments: adds users.department_id (nullable FK ->
departments.id ON DELETE SET NULL). Existing users keep NULL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c194aedf42a6'
down_revision: Union[str, None] = 'cfad24348323'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('department_id', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            'fk_users_department_id',
            'departments',
            ['department_id'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_department_id', type_='foreignkey')
        batch_op.drop_column('department_id')

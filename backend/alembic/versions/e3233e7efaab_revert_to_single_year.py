"""revert_to_single_year

Revision ID: e3233e7efaab
Revises: f252e0f937a1
Create Date: 2026-04-09 01:48:53.139866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3233e7efaab'
down_revision: Union[str, None] = 'f252e0f937a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add year_id column to categories (nullable for now)
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(sa.Column("year_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_categories_year_id", "years", ["year_id"], ["id"])

    # 2. Migrate data from year_categories junction table
    op.execute(
        "UPDATE categories SET year_id = ("
        "SELECT year_id FROM year_categories WHERE category_id = categories.id LIMIT 1"
        ")"
    )

    # 3. Drop year_categories table
    op.drop_table("year_categories")


def downgrade() -> None:
    # 1. Recreate year_categories table
    op.create_table(
        "year_categories",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("year_id", sa.Integer(), sa.ForeignKey("years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.String(length=36), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("year_id", "category_id"),
    )

    # 2. Migrate data back
    op.execute(
        "INSERT INTO year_categories (id, year_id, category_id) "
        "SELECT lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-' || hex(randomblob(2)) || '-' || hex(randomblob(2)) || '-' || hex(randomblob(6))), year_id, id FROM categories WHERE year_id IS NOT NULL"
    )

    # 3. Drop year_id column from categories
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_constraint("fk_categories_year_id", type_="foreignkey")
        batch_op.drop_column("year_id")

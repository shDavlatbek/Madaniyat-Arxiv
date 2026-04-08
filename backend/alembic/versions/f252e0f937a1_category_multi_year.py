"""category_multi_year

Revision ID: f252e0f937a1
Revises: e38e0f5634ef
Create Date: 2026-04-08 18:14:32.216684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f252e0f937a1'
down_revision: Union[str, None] = 'e38e0f5634ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Re-create year_categories junction table
    op.create_table(
        "year_categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("year_id", sa.Integer(), sa.ForeignKey("years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("year_id", "category_id"),
    )

    # 2. Migrate existing data from categories.year_id into year_categories
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "INSERT INTO year_categories (id, year_id, category_id) "
            "SELECT lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-' || hex(randomblob(2)) || '-' || hex(randomblob(2)) || '-' || hex(randomblob(6))), year_id, id "
            "FROM categories WHERE year_id IS NOT NULL"
        )
    )

    # 3. Drop year_id column from categories (batch for SQLite)
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_column("year_id")


def downgrade() -> None:
    # 1. Re-add year_id column to categories
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(sa.Column("year_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_categories_year_id", "years", ["year_id"], ["id"])

    # 2. Migrate data back from year_categories to categories.year_id
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE categories SET year_id = ("
            "  SELECT yc.year_id FROM year_categories yc"
            "  WHERE yc.category_id = categories.id"
            "  LIMIT 1"
            ") WHERE year_id IS NULL"
        )
    )

    # 3. Drop year_categories table
    op.drop_table("year_categories")

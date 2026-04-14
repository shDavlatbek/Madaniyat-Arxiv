"""category_year_direct_and_default_fields

Revision ID: e38e0f5634ef
Revises: 05215d4620e6
Create Date: 2026-04-08 16:40:41.143859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e38e0f5634ef'
down_revision: Union[str, None] = '05215d4620e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add year_id column to categories table
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(sa.Column("year_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_categories_year_id", "years", ["year_id"], ["id"])

    # 2. Create default_fields table
    op.create_table(
        "default_fields",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("field_type", sa.String(30), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("placeholder", sa.String(255), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
    )

    # 3. Migrate data from year_categories to categories.year_id
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

    # 4. Drop year_categories table
    op.drop_table("year_categories")


def downgrade() -> None:
    # Recreate year_categories table
    op.create_table(
        "year_categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("year_id", sa.Integer(), sa.ForeignKey("years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("year_id", "category_id"),
    )

    # Migrate data back
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "INSERT INTO year_categories (id, year_id, category_id) "
            "SELECT gen_random_uuid()::text, year_id, id "
            "FROM categories WHERE year_id IS NOT NULL"
        )
    )

    # Remove year_id from categories
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_column("year_id")

    # Drop default_fields table
    op.drop_table("default_fields")

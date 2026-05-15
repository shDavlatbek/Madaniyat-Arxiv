"""add_search_index_jobs_outbox

The outbox table the ``arq`` worker drains to keep Elasticsearch in sync with
Postgres. Native ``uuid`` columns on Postgres, ``String(36)`` on SQLite — same
pattern as the rest of the schema after migration ``2e1c76b0f45f``.

Revision ID: fd1de5d01d99
Revises: 2e1c76b0f45f
Create Date: 2026-05-15 20:15:11.617012

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "fd1de5d01d99"
down_revision: Union[str, None] = "2e1c76b0f45f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_guid_type = sa.String(length=36).with_variant(postgresql.UUID(as_uuid=True), "postgresql")


def upgrade() -> None:
    op.create_table(
        "search_index_jobs",
        sa.Column("id", _guid_type, nullable=False),
        sa.Column("document_id", _guid_type, nullable=False),
        sa.Column("op", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_search_index_jobs_created_at",
        "search_index_jobs",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_search_index_jobs_created_at", table_name="search_index_jobs")
    op.drop_table("search_index_jobs")

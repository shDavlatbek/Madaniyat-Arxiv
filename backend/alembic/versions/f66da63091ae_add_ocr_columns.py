"""add_ocr_columns

Revision ID: f66da63091ae
Revises: fd1de5d01d99
Create Date: 2026-05-15 20:33:27.891848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f66da63091ae'
down_revision: Union[str, None] = 'fd1de5d01d99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("ocr_status", sa.String(length=20), server_default="pending", nullable=False))
    op.add_column("documents", sa.Column("ocr_completed_at", sa.DateTime(), nullable=True))
    op.add_column("document_attachments", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("document_attachments", sa.Column("ocr_status", sa.String(length=20), server_default="pending", nullable=False))
    op.add_column("document_attachments", sa.Column("ocr_completed_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("document_attachments", "ocr_completed_at")
    op.drop_column("document_attachments", "ocr_status")
    op.drop_column("document_attachments", "extracted_text")
    op.drop_column("documents", "ocr_completed_at")
    op.drop_column("documents", "ocr_status")
    op.drop_column("documents", "extracted_text")

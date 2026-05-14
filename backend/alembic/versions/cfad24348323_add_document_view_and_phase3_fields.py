"""add_document_view_and_phase3_fields

Revision ID: cfad24348323
Revises: 9157aeada447
Create Date: 2026-05-14 19:49:40.365549

Adds the Phase 3 document-overhaul columns to `documents`:
- document_view (NOT NULL, server_default 'unknown' so existing rows backfill)
- archive_folder_id (FK -> archive_folders.id ON DELETE SET NULL)
- universal fields: document_form, sender, language, related_document_number/date
- view-specific fields: received_date, origin_organization, sent_date,
  recipient_organization, applicant_full_name, applicant_phone
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfad24348323'
down_revision: Union[str, None] = '9157aeada447'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_view', sa.String(length=20), server_default='unknown', nullable=False))
        batch_op.add_column(sa.Column('archive_folder_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('document_form', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('sender', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('language', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('related_document_number', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('related_document_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('received_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('origin_organization', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('sent_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('recipient_organization', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('applicant_full_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('applicant_phone', sa.String(length=50), nullable=True))
        batch_op.create_foreign_key(
            'fk_documents_archive_folder_id',
            'archive_folders',
            ['archive_folder_id'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_constraint('fk_documents_archive_folder_id', type_='foreignkey')
        batch_op.drop_column('applicant_phone')
        batch_op.drop_column('applicant_full_name')
        batch_op.drop_column('recipient_organization')
        batch_op.drop_column('sent_date')
        batch_op.drop_column('origin_organization')
        batch_op.drop_column('received_date')
        batch_op.drop_column('related_document_date')
        batch_op.drop_column('related_document_number')
        batch_op.drop_column('language')
        batch_op.drop_column('sender')
        batch_op.drop_column('document_form')
        batch_op.drop_column('archive_folder_id')
        batch_op.drop_column('document_view')

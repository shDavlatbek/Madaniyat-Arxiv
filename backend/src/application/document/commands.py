from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date

from src.domain.document.value_objects import DocumentView


@dataclass
class CreateDocumentCommand:
    year_id: int
    category_id: uuid.UUID
    title: str
    document_number: str
    date: date
    short_desc: str | None = None
    pages: int | None = None
    signer: str | None = None
    archive_number: str | None = None
    person_id: uuid.UUID | None = None
    created_by: uuid.UUID | None = None
    dynamic_fields: dict[str, str] = field(default_factory=dict)
    # Phase 3 — document view + universal fields
    document_view: DocumentView = DocumentView.UNKNOWN
    archive_folder_id: uuid.UUID | None = None
    document_type_id: uuid.UUID | None = None
    document_form: str | None = None
    sender: str | None = None
    language: str | None = None
    related_document_number: str | None = None
    related_document_date: date | None = None
    # Phase 3 — view-specific fields
    received_date: date | None = None
    origin_organization: str | None = None
    sent_date: date | None = None
    recipient_organization: str | None = None
    applicant_full_name: str | None = None
    applicant_phone: str | None = None
    # Murojaat (appeal) — reference FKs + extra fields
    region_id: uuid.UUID | None = None
    country_id: uuid.UUID | None = None
    reception_place_id: uuid.UUID | None = None
    appeal_type_id: uuid.UUID | None = None
    person_type: str | None = None
    outgoing_number: str | None = None
    outgoing_date: date | None = None
    signed_by: str | None = None
    note: str | None = None


@dataclass
class UpdateDocumentCommand:
    document_id: uuid.UUID
    category_id: uuid.UUID | None = None
    title: str | None = None
    document_number: str | None = None
    date: date | None = None
    short_desc: str | None = None
    pages: int | None = None
    signer: str | None = None
    archive_number: str | None = None
    person_id: uuid.UUID | None = None
    dynamic_fields: dict[str, str] | None = None
    # Phase 3 — document view + universal fields
    document_view: DocumentView | None = None
    archive_folder_id: uuid.UUID | None = None
    document_type_id: uuid.UUID | None = None
    document_form: str | None = None
    sender: str | None = None
    language: str | None = None
    related_document_number: str | None = None
    related_document_date: date | None = None
    # Phase 3 — view-specific fields
    received_date: date | None = None
    origin_organization: str | None = None
    sent_date: date | None = None
    recipient_organization: str | None = None
    applicant_full_name: str | None = None
    applicant_phone: str | None = None
    # Murojaat (appeal) — reference FKs + extra fields
    region_id: uuid.UUID | None = None
    country_id: uuid.UUID | None = None
    reception_place_id: uuid.UUID | None = None
    appeal_type_id: uuid.UUID | None = None
    person_type: str | None = None
    outgoing_number: str | None = None
    outgoing_date: date | None = None
    signed_by: str | None = None
    note: str | None = None


@dataclass
class DeleteDocumentCommand:
    document_id: uuid.UUID


@dataclass
class UploadFileCommand:
    document_id: uuid.UUID
    filename: str
    content: bytes


@dataclass
class UploadAttachmentCommand:
    document_id: uuid.UUID
    filename: str
    content: bytes
    sort_order: int = 0


@dataclass
class DeleteAttachmentCommand:
    document_id: uuid.UUID
    attachment_id: uuid.UUID

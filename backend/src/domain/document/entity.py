from __future__ import annotations

import uuid
from datetime import date, datetime

from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.document.value_objects import DocumentAttachment, DocumentFieldValue, DocumentView


class Document(AggregateRoot):
    def __init__(
        self,
        year_id: int,
        category_id: uuid.UUID,
        title: str,
        document_number: str,
        date: date,
        short_desc: str | None = None,
        pages: int | None = None,
        file_path: str | None = None,
        signer: str | None = None,
        archive_number: str | None = None,
        person_id: uuid.UUID | None = None,
        year_value: int | None = None,
        person_name: str | None = None,
        person_position: str | None = None,
        created_by: uuid.UUID | None = None,
        # Phase 3 — document view + universal fields
        document_view: DocumentView = DocumentView.UNKNOWN,
        archive_folder_id: uuid.UUID | None = None,
        document_type_id: uuid.UUID | None = None,
        document_type_name: str | None = None,
        document_form: str | None = None,
        sender: str | None = None,
        language: str | None = None,
        related_document_number: str | None = None,
        related_document_date: date | None = None,
        # Phase 3 — view-specific fields
        received_date: date | None = None,
        origin_organization: str | None = None,
        sent_date: date | None = None,
        recipient_organization: str | None = None,
        applicant_full_name: str | None = None,
        applicant_phone: str | None = None,
        # Murojaat (appeal) — reference FKs + extra fields
        region_id: uuid.UUID | None = None,
        country_id: uuid.UUID | None = None,
        reception_place_id: uuid.UUID | None = None,
        appeal_type_id: uuid.UUID | None = None,
        person_type: str | None = None,
        outgoing_number: str | None = None,
        outgoing_date: date | None = None,
        signed_by: str | None = None,
        note: str | None = None,
        field_values: list[DocumentFieldValue] | None = None,
        attachments: list[DocumentAttachment] | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.year_id = year_id
        self.category_id = category_id
        self.title = title
        self.document_number = document_number
        self.date = date
        self.short_desc = short_desc
        self.pages = pages
        self.file_path = file_path
        self.signer = signer
        self.archive_number = archive_number
        self.year_value = year_value
        self.person_id = person_id
        self.person_name = person_name
        self.person_position = person_position
        self.created_by = created_by
        self.document_view = document_view
        self.archive_folder_id = archive_folder_id
        self.document_type_id = document_type_id
        self.document_type_name = document_type_name
        self.document_form = document_form
        self.sender = sender
        self.language = language
        self.related_document_number = related_document_number
        self.related_document_date = related_document_date
        self.received_date = received_date
        self.origin_organization = origin_organization
        self.sent_date = sent_date
        self.recipient_organization = recipient_organization
        self.applicant_full_name = applicant_full_name
        self.applicant_phone = applicant_phone
        self.region_id = region_id
        self.country_id = country_id
        self.reception_place_id = reception_place_id
        self.appeal_type_id = appeal_type_id
        self.person_type = person_type
        self.outgoing_number = outgoing_number
        self.outgoing_date = outgoing_date
        self.signed_by = signed_by
        self.note = note
        self.field_values = field_values or []
        self.attachments = attachments or []

    def update(
        self,
        category_id: uuid.UUID | None = None,
        title: str | None = None,
        document_number: str | None = None,
        date: date | None = None,
        short_desc: str | None = None,
        pages: int | None = None,
        signer: str | None = None,
        archive_number: str | None = None,
        person_id: uuid.UUID | None = None,
        document_view: DocumentView | None = None,
        archive_folder_id: uuid.UUID | None = None,
        document_type_id: uuid.UUID | None = None,
        document_form: str | None = None,
        sender: str | None = None,
        language: str | None = None,
        related_document_number: str | None = None,
        related_document_date: date | None = None,
        received_date: date | None = None,
        origin_organization: str | None = None,
        sent_date: date | None = None,
        recipient_organization: str | None = None,
        applicant_full_name: str | None = None,
        applicant_phone: str | None = None,
        region_id: uuid.UUID | None = None,
        country_id: uuid.UUID | None = None,
        reception_place_id: uuid.UUID | None = None,
        appeal_type_id: uuid.UUID | None = None,
        person_type: str | None = None,
        outgoing_number: str | None = None,
        outgoing_date: date | None = None,
        signed_by: str | None = None,
        note: str | None = None,
    ) -> None:
        if category_id is not None:
            self.category_id = category_id
        if title is not None:
            self.title = title
        if document_number is not None:
            self.document_number = document_number
        if date is not None:
            self.date = date
        if short_desc is not None:
            self.short_desc = short_desc
        if pages is not None:
            self.pages = pages
        if signer is not None:
            self.signer = signer
        if archive_number is not None:
            self.archive_number = archive_number
        if person_id is not None:
            self.person_id = person_id
        if document_view is not None:
            self.document_view = document_view
        if archive_folder_id is not None:
            self.archive_folder_id = archive_folder_id
        if document_type_id is not None:
            self.document_type_id = document_type_id
        if document_form is not None:
            self.document_form = document_form
        if sender is not None:
            self.sender = sender
        if language is not None:
            self.language = language
        if related_document_number is not None:
            self.related_document_number = related_document_number
        if related_document_date is not None:
            self.related_document_date = related_document_date
        if received_date is not None:
            self.received_date = received_date
        if origin_organization is not None:
            self.origin_organization = origin_organization
        if sent_date is not None:
            self.sent_date = sent_date
        if recipient_organization is not None:
            self.recipient_organization = recipient_organization
        if applicant_full_name is not None:
            self.applicant_full_name = applicant_full_name
        if applicant_phone is not None:
            self.applicant_phone = applicant_phone
        if region_id is not None:
            self.region_id = region_id
        if country_id is not None:
            self.country_id = country_id
        if reception_place_id is not None:
            self.reception_place_id = reception_place_id
        if appeal_type_id is not None:
            self.appeal_type_id = appeal_type_id
        if person_type is not None:
            self.person_type = person_type
        if outgoing_number is not None:
            self.outgoing_number = outgoing_number
        if outgoing_date is not None:
            self.outgoing_date = outgoing_date
        if signed_by is not None:
            self.signed_by = signed_by
        if note is not None:
            self.note = note
        self.updated_at = datetime.utcnow()

    def set_field_values(self, field_values: list[DocumentFieldValue]) -> None:
        self.field_values = field_values
        self.updated_at = datetime.utcnow()

    def set_file_path(self, file_path: str) -> None:
        self.file_path = file_path
        self.updated_at = datetime.utcnow()

    def add_attachment(self, attachment: DocumentAttachment) -> None:
        self.attachments.append(attachment)
        self.updated_at = datetime.utcnow()

    def remove_attachment(self, attachment_id: uuid.UUID) -> None:
        self.attachments = [a for a in self.attachments if a.id != attachment_id]
        self.updated_at = datetime.utcnow()

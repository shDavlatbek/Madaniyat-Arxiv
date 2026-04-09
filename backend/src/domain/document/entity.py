from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.document.value_objects import DocumentAttachment, DocumentFieldValue


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
        self.updated_at = datetime.now(timezone.utc)

    def set_field_values(self, field_values: list[DocumentFieldValue]) -> None:
        self.field_values = field_values
        self.updated_at = datetime.now(timezone.utc)

    def set_file_path(self, file_path: str) -> None:
        self.file_path = file_path
        self.updated_at = datetime.now(timezone.utc)

    def add_attachment(self, attachment: DocumentAttachment) -> None:
        self.attachments.append(attachment)
        self.updated_at = datetime.now(timezone.utc)

    def remove_attachment(self, attachment_id: uuid.UUID) -> None:
        self.attachments = [a for a in self.attachments if a.id != attachment_id]
        self.updated_at = datetime.now(timezone.utc)

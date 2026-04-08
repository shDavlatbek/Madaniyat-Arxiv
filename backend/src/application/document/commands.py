from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date


@dataclass
class CreateDocumentCommand:
    year_id: int
    category_id: uuid.UUID
    title: str
    document_number: str
    date: date
    short_desc: str | None = None
    target: str | None = None
    pages: int | None = None
    signer: str | None = None
    created_by: uuid.UUID | None = None
    dynamic_fields: dict[str, str] = field(default_factory=dict)


@dataclass
class UpdateDocumentCommand:
    document_id: uuid.UUID
    title: str | None = None
    document_number: str | None = None
    date: date | None = None
    short_desc: str | None = None
    target: str | None = None
    pages: int | None = None
    signer: str | None = None
    dynamic_fields: dict[str, str] | None = None


@dataclass
class DeleteDocumentCommand:
    document_id: uuid.UUID


@dataclass
class UploadFileCommand:
    document_id: uuid.UUID
    filename: str
    content: bytes

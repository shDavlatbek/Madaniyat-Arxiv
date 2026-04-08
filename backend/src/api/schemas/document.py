from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class CreateDocumentRequest(BaseModel):
    year_id: int
    category_id: uuid.UUID
    title: str = Field(min_length=1, max_length=500)
    document_number: str = Field(min_length=1, max_length=100)
    date: date
    short_desc: str | None = None
    target: str | None = None
    pages: int | None = Field(default=None, ge=0)
    signer: str | None = None
    dynamic_fields: dict[str, str] = Field(default_factory=dict)


class UpdateDocumentRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    document_number: str | None = Field(default=None, min_length=1, max_length=100)
    date: date | None = None
    short_desc: str | None = None
    target: str | None = None
    pages: int | None = Field(default=None, ge=0)
    signer: str | None = None
    dynamic_fields: dict[str, str] | None = None


class DocumentFieldValueResponse(BaseModel):
    category_field_id: uuid.UUID
    value: str | None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    year_id: int
    category_id: uuid.UUID
    title: str
    document_number: str
    date: date
    short_desc: str | None
    target: str | None
    pages: int | None
    file_path: str | None
    signer: str | None
    created_by: uuid.UUID | None
    field_values: list[DocumentFieldValueResponse]
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int

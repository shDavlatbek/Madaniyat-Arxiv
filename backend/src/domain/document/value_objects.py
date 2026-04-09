from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class DocumentNumber(ValueObject):
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Document number cannot be empty")


@dataclass(frozen=True)
class DocumentFieldValue(ValueObject):
    category_field_id: uuid.UUID
    value: str | None
    id: uuid.UUID | None = None


@dataclass
class DocumentAttachment:
    document_id: uuid.UUID
    file_path: str
    original_filename: str
    sort_order: int = 0
    id: uuid.UUID | None = None
    created_at: object | None = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid.uuid4()

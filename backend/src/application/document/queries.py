from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from src.domain.document.value_objects import DocumentView


@dataclass
class ListDocumentsQuery:
    category_id: uuid.UUID | None = None
    search: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    field_filters: dict[str, str] = field(default_factory=dict)
    document_view: DocumentView | None = None
    archive_folder_id: uuid.UUID | None = None
    page: int = 1
    page_size: int = 20


@dataclass
class GetDocumentQuery:
    document_id: uuid.UUID

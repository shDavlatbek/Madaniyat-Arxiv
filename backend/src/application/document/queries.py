from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class ListDocumentsQuery:
    year_id: int | None = None
    category_id: uuid.UUID | None = None
    search: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    field_filters: dict[str, str] = field(default_factory=dict)
    page: int = 1
    page_size: int = 20


@dataclass
class GetDocumentQuery:
    document_id: uuid.UUID

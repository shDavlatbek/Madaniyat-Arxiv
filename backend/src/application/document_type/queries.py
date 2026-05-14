from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class ListDocumentTypesQuery:
    search: str | None = None


@dataclass
class GetDocumentTypeQuery:
    document_type_id: uuid.UUID

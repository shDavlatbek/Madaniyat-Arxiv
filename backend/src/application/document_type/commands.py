from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class CreateDocumentTypeCommand:
    name: str


@dataclass
class UpdateDocumentTypeCommand:
    document_type_id: uuid.UUID
    name: str | None = None


@dataclass
class DeleteDocumentTypeCommand:
    document_type_id: uuid.UUID

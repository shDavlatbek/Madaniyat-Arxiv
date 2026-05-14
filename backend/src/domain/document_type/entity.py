from __future__ import annotations

import uuid
from datetime import datetime

from src.domain.shared.entity import Entity


class DocumentType(Entity):
    """Hujjat turi — a reference taxonomy entry classifying a document."""

    def __init__(
        self,
        name: str,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        if not name or not name.strip():
            raise ValueError("Document type name cannot be empty")
        self.name = name.strip()

    def update(self, name: str | None = None) -> None:
        if name is not None:
            if not name.strip():
                raise ValueError("Document type name cannot be empty")
            self.name = name.strip()
        self.updated_at = datetime.utcnow()

from __future__ import annotations

import uuid
from datetime import datetime

from src.domain.shared.entity import Entity


class MusicSchool(Entity):
    def __init__(
        self,
        name: str,
        code: str | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        if not name or not name.strip():
            raise ValueError("Music school name cannot be empty")
        self.name = name.strip()
        self.code = code.strip() if code else None

    def update(
        self,
        name: str | None = None,
        code: str | None = None,
    ) -> None:
        if name is not None:
            if not name.strip():
                raise ValueError("Music school name cannot be empty")
            self.name = name.strip()
        if code is not None:
            self.code = code.strip() or None
        self.updated_at = datetime.utcnow()

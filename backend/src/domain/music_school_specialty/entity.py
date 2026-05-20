from __future__ import annotations

import uuid
from datetime import datetime

from src.domain.shared.entity import Entity


class MusicSchoolSpecialty(Entity):
    def __init__(
        self,
        music_school_id: uuid.UUID,
        name: str,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        if not music_school_id:
            raise ValueError("Music school ID is required")
        if not name or not name.strip():
            raise ValueError("Specialty name cannot be empty")
        self.music_school_id = music_school_id
        self.name = name.strip()

    def update(self, name: str | None = None) -> None:
        if name is not None:
            if not name.strip():
                raise ValueError("Specialty name cannot be empty")
            self.name = name.strip()
        self.updated_at = datetime.utcnow()

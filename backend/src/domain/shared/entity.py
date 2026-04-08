from __future__ import annotations

import uuid
from datetime import datetime, timezone


class Entity:
    def __init__(self, id: uuid.UUID | None = None, created_at: datetime | None = None, updated_at: datetime | None = None):
        self.id = id or uuid.uuid4()
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

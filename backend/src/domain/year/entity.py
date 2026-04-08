from __future__ import annotations

from datetime import datetime

from src.domain.shared.entity import Entity


class Year(Entity):
    def __init__(
        self,
        value: int,
        is_active: bool = True,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        # Year uses integer IDs, not UUID
        self.id = id
        self.value = value
        self.is_active = is_active
        self.created_at = created_at or datetime.now(__import__('datetime').timezone.utc)
        self.updated_at = updated_at or datetime.now(__import__('datetime').timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Year):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

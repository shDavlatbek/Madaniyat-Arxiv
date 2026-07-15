from __future__ import annotations

import uuid
from datetime import datetime

from src.domain.shared.entity import Entity


class Department(Entity):
    def __init__(
        self,
        name: str,
        index_code: str | None = None,
        description: str | None = None,
        is_active: bool = True,
        year_id: int | None = None,
        year_value: int | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        if not name or not name.strip():
            raise ValueError("Department name cannot be empty")
        self.name = name.strip()
        self.index_code = index_code.strip() if index_code else None
        self.description = description
        self.is_active = is_active
        self.year_id = year_id
        # Denormalized display field populated by the mapper (years.value).
        self.year_value = year_value

    def update(
        self,
        name: str | None = None,
        index_code: str | None = None,
        description: str | None = None,
        year_id: int | None = None,
    ) -> None:
        if name is not None:
            if not name.strip():
                raise ValueError("Department name cannot be empty")
            self.name = name.strip()
        if index_code is not None:
            self.index_code = index_code.strip() or None
        if description is not None:
            self.description = description
        if year_id is not None:
            self.year_id = year_id
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.utcnow()

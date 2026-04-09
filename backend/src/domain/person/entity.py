from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from src.domain.shared.entity import Entity


class PersonTenure:
    def __init__(
        self,
        person_id: uuid.UUID,
        position: str,
        start_date: date,
        end_date: date | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id or uuid.uuid4()
        self.person_id = person_id
        self.position = position
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at or datetime.now(timezone.utc)


class Person(Entity):
    def __init__(
        self,
        full_name: str,
        tenures: list[PersonTenure] | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.full_name = full_name
        self.tenures = tenures or []

    def update(self, full_name: str | None = None) -> None:
        if full_name is not None:
            self.full_name = full_name
        self.updated_at = datetime.now(timezone.utc)

    def set_tenures(self, tenures: list[PersonTenure]) -> None:
        self.tenures = tenures
        self.updated_at = datetime.now(timezone.utc)

    def active_tenure_on(self, d: date) -> PersonTenure | None:
        for t in self.tenures:
            if t.start_date <= d and (t.end_date is None or t.end_date >= d):
                return t
        return None

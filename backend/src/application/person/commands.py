from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date


@dataclass
class TenureData:
    position: str
    start_date: date
    end_date: date | None = None


@dataclass
class CreatePersonCommand:
    full_name: str
    tenures: list[TenureData] = field(default_factory=list)


@dataclass
class UpdatePersonCommand:
    person_id: uuid.UUID
    full_name: str | None = None
    tenures: list[TenureData] | None = None


@dataclass
class DeletePersonCommand:
    person_id: uuid.UUID

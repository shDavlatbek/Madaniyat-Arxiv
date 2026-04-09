from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date


@dataclass
class ListPersonsQuery:
    search: str | None = None


@dataclass
class GetPersonQuery:
    person_id: uuid.UUID


@dataclass
class ListActivePersonsOnDateQuery:
    date: date

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import date

from src.domain.person.entity import Person


class PersonRepository(ABC):
    @abstractmethod
    async def find_by_id(self, person_id: uuid.UUID) -> Person | None: ...

    @abstractmethod
    async def find_all(self, search: str | None = None) -> list[Person]: ...

    @abstractmethod
    async def find_active_on_date(self, d: date) -> list[Person]: ...

    @abstractmethod
    async def save(self, person: Person) -> Person: ...

    @abstractmethod
    async def delete(self, person_id: uuid.UUID) -> None: ...

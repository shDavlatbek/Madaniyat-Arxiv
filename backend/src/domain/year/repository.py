from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.year.entity import Year


class YearRepository(ABC):
    @abstractmethod
    async def find_all(self, active_only: bool = True) -> list[Year]: ...

    @abstractmethod
    async def find_by_id(self, year_id: int) -> Year | None: ...

    @abstractmethod
    async def find_by_value(self, value: int) -> Year | None: ...

    @abstractmethod
    async def save(self, year: Year) -> Year: ...

    @abstractmethod
    async def delete(self, year_id: int) -> None: ...

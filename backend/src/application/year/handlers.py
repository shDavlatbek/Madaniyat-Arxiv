from __future__ import annotations

from src.domain.shared.errors import NotFoundError, ValidationError
from src.domain.year.entity import Year
from src.domain.year.repository import YearRepository

from .commands import CreateYearCommand, DeleteYearCommand, UpdateYearCommand
from .queries import ListYearsQuery


class YearCommandHandler:
    def __init__(self, year_repo: YearRepository):
        self._year_repo = year_repo

    async def create(self, command: CreateYearCommand) -> Year:
        existing = await self._year_repo.find_by_value(command.value)
        if existing:
            raise ValidationError(f"Year {command.value} already exists")
        year = Year(value=command.value, is_active=command.is_active)
        return await self._year_repo.save(year)

    async def update(self, command: UpdateYearCommand) -> Year:
        year = await self._year_repo.find_by_id(command.year_id)
        if not year:
            raise NotFoundError("Year", str(command.year_id))
        if command.value is not None:
            year.value = command.value
        if command.is_active is not None:
            year.is_active = command.is_active
        return await self._year_repo.save(year)

    async def delete(self, command: DeleteYearCommand) -> None:
        await self._year_repo.delete(command.year_id)


class YearQueryHandler:
    def __init__(self, year_repo: YearRepository):
        self._year_repo = year_repo

    async def list_years(self, query: ListYearsQuery) -> list[Year]:
        return await self._year_repo.find_all(active_only=query.active_only)

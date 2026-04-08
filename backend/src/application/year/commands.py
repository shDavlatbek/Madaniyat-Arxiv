from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CreateYearCommand:
    value: int
    is_active: bool = True


@dataclass
class UpdateYearCommand:
    year_id: int
    value: int | None = None
    is_active: bool | None = None


@dataclass
class DeleteYearCommand:
    year_id: int

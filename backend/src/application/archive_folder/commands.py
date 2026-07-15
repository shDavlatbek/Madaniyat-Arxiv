from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date


@dataclass
class CreateArchiveFolderCommand:
    index_code: str
    title: str
    department_id: uuid.UUID | None = None
    article_number: str | None = None
    list_number: str | None = None
    note: str | None = None
    retention_period_id: uuid.UUID | None = None
    total_sheets: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    year_id: int | None = None


@dataclass
class UpdateArchiveFolderCommand:
    folder_id: uuid.UUID
    index_code: str | None = None
    title: str | None = None
    department_id: uuid.UUID | None = None
    article_number: str | None = None
    list_number: str | None = None
    note: str | None = None
    retention_period_id: uuid.UUID | None = None
    total_sheets: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    year_id: int | None = None


@dataclass
class DeleteArchiveFolderCommand:
    folder_id: uuid.UUID

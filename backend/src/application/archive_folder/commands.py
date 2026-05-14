from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from src.domain.archive_folder.value_objects import RetentionPeriod


@dataclass
class CreateArchiveFolderCommand:
    index_code: str
    title: str
    retention_period: RetentionPeriod
    start_date: date
    end_date: date | None = None
    year_id: int | None = None


@dataclass
class UpdateArchiveFolderCommand:
    folder_id: uuid.UUID
    index_code: str | None = None
    title: str | None = None
    retention_period: RetentionPeriod | None = None
    start_date: date | None = None
    end_date: date | None = None
    year_id: int | None = None


@dataclass
class DeleteArchiveFolderCommand:
    folder_id: uuid.UUID

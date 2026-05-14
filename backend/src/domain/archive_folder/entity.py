from __future__ import annotations

import uuid
from datetime import date, datetime

from src.domain.archive_folder.value_objects import RetentionPeriod
from src.domain.shared.entity import Entity
from src.domain.shared.errors import ValidationError


class ArchiveFolder(Entity):
    """Yig'ma jild — a collected folder grouping documents within a year."""

    def __init__(
        self,
        index_code: str,
        title: str,
        retention_period: RetentionPeriod,
        start_date: date,
        end_date: date | None = None,
        year_id: int | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        if not index_code or not index_code.strip():
            raise ValidationError("Archive folder index_code cannot be empty")
        if not title or not title.strip():
            raise ValidationError("Archive folder title cannot be empty")
        if end_date is not None and end_date < start_date:
            raise ValidationError("Archive folder end_date cannot precede start_date")
        self.index_code = index_code.strip()
        self.title = title.strip()
        self.retention_period = retention_period
        self.start_date = start_date
        self.end_date = end_date
        self.year_id = year_id

    def update(
        self,
        index_code: str | None = None,
        title: str | None = None,
        retention_period: RetentionPeriod | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        year_id: int | None = None,
    ) -> None:
        if index_code is not None:
            if not index_code.strip():
                raise ValidationError("Archive folder index_code cannot be empty")
            self.index_code = index_code.strip()
        if title is not None:
            if not title.strip():
                raise ValidationError("Archive folder title cannot be empty")
            self.title = title.strip()
        if retention_period is not None:
            self.retention_period = retention_period
        if start_date is not None:
            self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date
        if year_id is not None:
            self.year_id = year_id
        effective_end = self.end_date
        if effective_end is not None and effective_end < self.start_date:
            raise ValidationError("Archive folder end_date cannot precede start_date")
        self.updated_at = datetime.utcnow()

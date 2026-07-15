from __future__ import annotations

import uuid
from datetime import date, datetime

from src.domain.shared.entity import Entity
from src.domain.shared.errors import ValidationError


class ArchiveFolder(Entity):
    """Yig'ma jild — a collected folder grouping documents within a year.

    Surface fields (per partner-system contract):
      Bo'lim nomi          -> department_id (FK)
      Bo'lim indeksi       -> denormalized department_index_code (read-only)
      Yig'ma jild indeksi  -> index_code
      Yig'ma jild sarlavhasi -> title
      Modda raqami         -> article_number
      Saqlash muddati      -> retention_period_id (FK)
      Eslatma              -> note

    Legacy date / year fields stay on the entity for backward compatibility
    with existing rows but are no longer exposed by the form.
    """

    def __init__(
        self,
        index_code: str,
        title: str,
        department_id: uuid.UUID | None = None,
        department_name: str | None = None,
        department_index_code: str | None = None,
        article_number: str | None = None,
        list_number: str | None = None,
        note: str | None = None,
        retention_period_id: uuid.UUID | None = None,
        retention_period_name: str | None = None,
        total_sheets: int | None = None,
        start_date: date | None = None,
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
        if start_date is not None and end_date is not None and end_date < start_date:
            raise ValidationError("Archive folder end_date cannot precede start_date")
        self.index_code = index_code.strip()
        self.title = title.strip()
        self.department_id = department_id
        self.article_number = article_number.strip() if article_number else None
        self.list_number = list_number.strip() if list_number else None
        self.note = note
        self.retention_period_id = retention_period_id
        self.total_sheets = total_sheets
        # Denormalized display fields populated by the mapper.
        self.department_name = department_name
        self.department_index_code = department_index_code
        self.retention_period_name = retention_period_name
        self.start_date = start_date
        self.end_date = end_date
        self.year_id = year_id

    def update(
        self,
        index_code: str | None = None,
        title: str | None = None,
        department_id: uuid.UUID | None = None,
        article_number: str | None = None,
        list_number: str | None = None,
        note: str | None = None,
        retention_period_id: uuid.UUID | None = None,
        total_sheets: int | None = None,
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
        if department_id is not None:
            self.department_id = department_id
        if article_number is not None:
            self.article_number = article_number.strip() or None
        if list_number is not None:
            self.list_number = list_number.strip() or None
        if note is not None:
            self.note = note
        if retention_period_id is not None:
            self.retention_period_id = retention_period_id
        if total_sheets is not None:
            self.total_sheets = total_sheets
        if start_date is not None:
            self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date
        if year_id is not None:
            self.year_id = year_id
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValidationError("Archive folder end_date cannot precede start_date")
        self.updated_at = datetime.utcnow()

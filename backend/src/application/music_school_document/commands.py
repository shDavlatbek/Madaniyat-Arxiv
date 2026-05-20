from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateMusicSchoolDocumentCommand:
    student_full_name: str
    music_school_id: uuid.UUID
    specialty_id: uuid.UUID
    graduation_year: int
    diploma_serial: str
    diploma_number: str
    given_date: dt.date
    description: str | None = None
    created_by: uuid.UUID | None = None


@dataclass(frozen=True)
class UpdateMusicSchoolDocumentCommand:
    document_id: uuid.UUID
    student_full_name: str | None = None
    music_school_id: uuid.UUID | None = None
    specialty_id: uuid.UUID | None = None
    graduation_year: int | None = None
    diploma_serial: str | None = None
    diploma_number: str | None = None
    given_date: dt.date | None = None
    description: str | None = None


@dataclass(frozen=True)
class DeleteMusicSchoolDocumentCommand:
    document_id: uuid.UUID


@dataclass(frozen=True)
class UploadMusicSchoolDocumentFileCommand:
    document_id: uuid.UUID
    content: bytes
    filename: str

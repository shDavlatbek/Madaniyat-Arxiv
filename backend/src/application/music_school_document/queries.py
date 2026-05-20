from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class GetMusicSchoolDocumentQuery:
    document_id: uuid.UUID


@dataclass(frozen=True)
class ListMusicSchoolDocumentsQuery:
    page: int = 1
    page_size: int = 20
    music_school_id: uuid.UUID | None = None
    graduation_year: int | None = None
    specialty_id: uuid.UUID | None = None
    search: str | None = None

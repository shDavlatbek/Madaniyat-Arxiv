from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.music_school_document.entity import MusicSchoolDocument


class MusicSchoolDocumentRepository(ABC):
    @abstractmethod
    async def find_by_id(self, document_id: uuid.UUID) -> MusicSchoolDocument | None: ...

    @abstractmethod
    async def find_all(
        self,
        page: int = 1,
        page_size: int = 20,
        music_school_id: uuid.UUID | None = None,
        graduation_year: int | None = None,
        specialty: str | None = None,
        search: str | None = None,
    ) -> tuple[list[MusicSchoolDocument], int]: ...

    @abstractmethod
    async def save(self, document: MusicSchoolDocument) -> MusicSchoolDocument: ...

    @abstractmethod
    async def delete(self, document_id: uuid.UUID) -> None: ...

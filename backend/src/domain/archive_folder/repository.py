from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.archive_folder.entity import ArchiveFolder


class ArchiveFolderRepository(ABC):
    @abstractmethod
    async def find_by_id(self, folder_id: uuid.UUID) -> ArchiveFolder | None: ...

    @abstractmethod
    async def find_by_index_code(self, year_id: int | None, index_code: str) -> ArchiveFolder | None: ...

    @abstractmethod
    async def find_all_with_counts(
        self, year_id: int | None = None, search: str | None = None
    ) -> list[tuple[ArchiveFolder, int, int]]:
        """Return (folder, document_count, documents_pages_sum) tuples in one round-trip."""
        ...

    @abstractmethod
    async def save(self, folder: ArchiveFolder) -> ArchiveFolder: ...

    @abstractmethod
    async def delete(self, folder_id: uuid.UUID) -> None: ...

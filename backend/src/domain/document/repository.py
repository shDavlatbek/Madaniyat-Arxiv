from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.domain.document.entity import Document


@dataclass
class DocumentSearchParams:
    year_id: int | None = None
    category_id: uuid.UUID | None = None
    search: str | None = None
    field_filters: dict[str, str] | None = None
    page: int = 1
    page_size: int = 20


class DocumentRepository(ABC):
    @abstractmethod
    async def find_by_id(self, document_id: uuid.UUID) -> Document | None: ...

    @abstractmethod
    async def search(self, params: DocumentSearchParams) -> tuple[list[Document], int]: ...

    @abstractmethod
    async def save(self, document: Document) -> Document: ...

    @abstractmethod
    async def delete(self, document_id: uuid.UUID) -> None: ...

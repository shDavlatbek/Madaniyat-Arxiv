from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.document_type.entity import DocumentType


class DocumentTypeRepository(ABC):
    @abstractmethod
    async def find_by_id(self, document_type_id: uuid.UUID) -> DocumentType | None: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> DocumentType | None: ...

    @abstractmethod
    async def find_all(self, search: str | None = None) -> list[DocumentType]: ...

    @abstractmethod
    async def save(self, document_type: DocumentType) -> DocumentType: ...

    @abstractmethod
    async def delete(self, document_type_id: uuid.UUID) -> None: ...

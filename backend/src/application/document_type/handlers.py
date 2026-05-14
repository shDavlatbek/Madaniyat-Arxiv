from __future__ import annotations

from src.domain.document_type.entity import DocumentType
from src.domain.document_type.repository import DocumentTypeRepository
from src.domain.shared.errors import NotFoundError, ValidationError

from .commands import (
    CreateDocumentTypeCommand,
    DeleteDocumentTypeCommand,
    UpdateDocumentTypeCommand,
)
from .queries import GetDocumentTypeQuery, ListDocumentTypesQuery


class DocumentTypeCommandHandler:
    def __init__(self, document_type_repo: DocumentTypeRepository):
        self._document_type_repo = document_type_repo

    async def create(self, command: CreateDocumentTypeCommand) -> DocumentType:
        existing = await self._document_type_repo.find_by_name(command.name.strip())
        if existing:
            raise ValidationError(f"Document type '{command.name}' already exists")
        document_type = DocumentType(name=command.name)
        return await self._document_type_repo.save(document_type)

    async def update(self, command: UpdateDocumentTypeCommand) -> DocumentType:
        document_type = await self._document_type_repo.find_by_id(command.document_type_id)
        if not document_type:
            raise NotFoundError("DocumentType", str(command.document_type_id))
        if command.name is not None and command.name.strip() != document_type.name:
            clash = await self._document_type_repo.find_by_name(command.name.strip())
            if clash and clash.id != document_type.id:
                raise ValidationError(f"Document type '{command.name}' already exists")
        document_type.update(name=command.name)
        return await self._document_type_repo.save(document_type)

    async def delete(self, command: DeleteDocumentTypeCommand) -> None:
        document_type = await self._document_type_repo.find_by_id(command.document_type_id)
        if not document_type:
            raise NotFoundError("DocumentType", str(command.document_type_id))
        await self._document_type_repo.delete(command.document_type_id)


class DocumentTypeQueryHandler:
    def __init__(self, document_type_repo: DocumentTypeRepository):
        self._document_type_repo = document_type_repo

    async def list_document_types(self, query: ListDocumentTypesQuery) -> list[DocumentType]:
        return await self._document_type_repo.find_all(search=query.search)

    async def get_document_type(self, query: GetDocumentTypeQuery) -> DocumentType:
        document_type = await self._document_type_repo.find_by_id(query.document_type_id)
        if not document_type:
            raise NotFoundError("DocumentType", str(query.document_type_id))
        return document_type

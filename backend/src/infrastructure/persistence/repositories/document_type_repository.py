import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.document_type.entity import DocumentType
from src.domain.document_type.repository import DocumentTypeRepository
from src.infrastructure.persistence.mappers.document_type_mapper import DocumentTypeMapper
from src.infrastructure.persistence.models import DocumentTypeModel


class SqlAlchemyDocumentTypeRepository(DocumentTypeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, document_type_id: uuid.UUID) -> DocumentType | None:
        model = await self._session.get(DocumentTypeModel, document_type_id)
        return DocumentTypeMapper.to_domain(model) if model else None

    async def find_by_name(self, name: str) -> DocumentType | None:
        stmt = select(DocumentTypeModel).where(DocumentTypeModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DocumentTypeMapper.to_domain(model) if model else None

    async def find_all(self, search: str | None = None) -> list[DocumentType]:
        stmt = select(DocumentTypeModel)
        if search:
            stmt = stmt.where(DocumentTypeModel.name.ilike(f"%{search}%"))
        stmt = stmt.order_by(DocumentTypeModel.name)
        result = await self._session.execute(stmt)
        return [DocumentTypeMapper.to_domain(m) for m in result.scalars().all()]

    async def save(self, document_type: DocumentType) -> DocumentType:
        existing = await self._session.get(DocumentTypeModel, document_type.id)
        if existing:
            DocumentTypeMapper.update_model(existing, document_type)
            await self._session.flush()
            await self._session.refresh(existing)
            return DocumentTypeMapper.to_domain(existing)
        model = DocumentTypeMapper.to_model(document_type)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return DocumentTypeMapper.to_domain(model)

    async def delete(self, document_type_id: uuid.UUID) -> None:
        model = await self._session.get(DocumentTypeModel, document_type_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

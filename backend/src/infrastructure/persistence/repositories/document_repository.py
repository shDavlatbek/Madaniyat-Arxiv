import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.document.entity import Document
from src.domain.document.repository import DocumentRepository, DocumentSearchParams
from src.infrastructure.persistence.mappers.document_mapper import DocumentMapper
from src.infrastructure.persistence.models import (
    CategoryFieldModel,
    DocumentAttachmentModel,
    DocumentFieldValueModel,
    DocumentModel,
    PersonModel,
    YearModel,
)


class SqlAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, document_id: uuid.UUID) -> Document | None:
        stmt = (
            select(DocumentModel)
            .where(DocumentModel.id == document_id)
            .options(selectinload(DocumentModel.field_values), selectinload(DocumentModel.attachments), selectinload(DocumentModel.year), selectinload(DocumentModel.person).selectinload(PersonModel.tenures))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DocumentMapper.to_domain(model) if model else None

    async def search(self, params: DocumentSearchParams) -> tuple[list[Document], int]:
        stmt = select(DocumentModel).options(selectinload(DocumentModel.field_values), selectinload(DocumentModel.attachments), selectinload(DocumentModel.year), selectinload(DocumentModel.person).selectinload(PersonModel.tenures))
        count_stmt = select(func.count()).select_from(DocumentModel)

        if params.year_id:
            stmt = stmt.where(DocumentModel.year_id == params.year_id)
            count_stmt = count_stmt.where(DocumentModel.year_id == params.year_id)

        if params.category_id:
            stmt = stmt.where(DocumentModel.category_id == params.category_id)
            count_stmt = count_stmt.where(DocumentModel.category_id == params.category_id)

        if params.date_from:
            stmt = stmt.where(DocumentModel.date >= params.date_from)
            count_stmt = count_stmt.where(DocumentModel.date >= params.date_from)

        if params.date_to:
            stmt = stmt.where(DocumentModel.date <= params.date_to)
            count_stmt = count_stmt.where(DocumentModel.date <= params.date_to)

        if params.search:
            search_filter = or_(
                DocumentModel.title.ilike(f"%{params.search}%"),
                DocumentModel.document_number.ilike(f"%{params.search}%"),
                DocumentModel.short_desc.ilike(f"%{params.search}%"),
                DocumentModel.signer.ilike(f"%{params.search}%"),
                DocumentModel.archive_number.ilike(f"%{params.search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        # Dynamic field filters
        if params.field_filters:
            for field_name, field_value in params.field_filters.items():
                subquery = (
                    select(DocumentFieldValueModel.document_id)
                    .join(CategoryFieldModel, CategoryFieldModel.id == DocumentFieldValueModel.category_field_id)
                    .where(
                        CategoryFieldModel.name == field_name,
                        DocumentFieldValueModel.value.ilike(f"%{field_value}%"),
                    )
                )
                stmt = stmt.where(DocumentModel.id.in_(subquery))
                count_stmt = count_stmt.where(DocumentModel.id.in_(subquery))

        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(DocumentModel.date.desc(), DocumentModel.created_at.desc())
        stmt = stmt.offset((params.page - 1) * params.page_size).limit(params.page_size)

        result = await self._session.execute(stmt)
        models = result.scalars().unique().all()

        return [DocumentMapper.to_domain(m) for m in models], total

    async def save(self, document: Document) -> Document:
        existing = await self._session.get(DocumentModel, document.id)
        if existing:
            DocumentMapper.update_model(existing, document)
            # Update field values: delete old, insert new
            await self._session.execute(
                DocumentFieldValueModel.__table__.delete().where(
                    DocumentFieldValueModel.document_id == document.id
                )
            )
            await self._session.flush()
            for fv in document.field_values:
                fv_model = DocumentMapper.field_value_to_model(document.id, fv)
                self._session.add(fv_model)
            # Update attachments: delete old, insert new
            await self._session.execute(
                DocumentAttachmentModel.__table__.delete().where(
                    DocumentAttachmentModel.document_id == document.id
                )
            )
            for att in document.attachments:
                self._session.add(DocumentMapper.attachment_to_model(att))
            await self._session.flush()
            # Reload
            stmt = (
                select(DocumentModel)
                .where(DocumentModel.id == document.id)
                .options(selectinload(DocumentModel.field_values), selectinload(DocumentModel.attachments), selectinload(DocumentModel.year), selectinload(DocumentModel.person).selectinload(PersonModel.tenures))
            )
            result = await self._session.execute(stmt)
            return DocumentMapper.to_domain(result.scalar_one())
        else:
            model = DocumentMapper.to_model(document)
            self._session.add(model)
            await self._session.flush()
            for fv in document.field_values:
                fv_model = DocumentMapper.field_value_to_model(model.id, fv)
                self._session.add(fv_model)
            for att in document.attachments:
                att.document_id = model.id
                self._session.add(DocumentMapper.attachment_to_model(att))
            await self._session.flush()
            # Reload
            stmt = (
                select(DocumentModel)
                .where(DocumentModel.id == model.id)
                .options(selectinload(DocumentModel.field_values), selectinload(DocumentModel.attachments), selectinload(DocumentModel.year), selectinload(DocumentModel.person).selectinload(PersonModel.tenures))
            )
            result = await self._session.execute(stmt)
            return DocumentMapper.to_domain(result.scalar_one())

    async def delete(self, document_id: uuid.UUID) -> None:
        model = await self._session.get(DocumentModel, document_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

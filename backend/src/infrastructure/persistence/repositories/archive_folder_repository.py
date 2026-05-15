import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.archive_folder.entity import ArchiveFolder
from src.domain.archive_folder.repository import ArchiveFolderRepository
from src.infrastructure.persistence.mappers.archive_folder_mapper import ArchiveFolderMapper
from src.infrastructure.persistence.models import ArchiveFolderModel, DocumentModel


class SqlAlchemyArchiveFolderRepository(ArchiveFolderRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, folder_id: uuid.UUID) -> ArchiveFolder | None:
        stmt = (
            select(ArchiveFolderModel)
            .options(selectinload(ArchiveFolderModel.retention_period))
            .where(ArchiveFolderModel.id == folder_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ArchiveFolderMapper.to_domain(model) if model else None

    async def find_by_index_code(self, year_id: int | None, index_code: str) -> ArchiveFolder | None:
        stmt = (
            select(ArchiveFolderModel)
            .options(selectinload(ArchiveFolderModel.retention_period))
            .where(
                ArchiveFolderModel.year_id.is_(year_id) if year_id is None
                else ArchiveFolderModel.year_id == year_id,
                ArchiveFolderModel.index_code == index_code,
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ArchiveFolderMapper.to_domain(model) if model else None

    async def find_all_with_counts(
        self, year_id: int | None = None, search: str | None = None
    ) -> list[tuple[ArchiveFolder, int]]:
        # Single round-trip: LEFT JOIN documents + COUNT, grouped per folder.
        stmt = (
            select(ArchiveFolderModel, func.count(DocumentModel.id))
            .outerjoin(DocumentModel, DocumentModel.archive_folder_id == ArchiveFolderModel.id)
            .options(selectinload(ArchiveFolderModel.retention_period))
            .group_by(ArchiveFolderModel.id)
        )
        if year_id is not None:
            stmt = stmt.where(ArchiveFolderModel.year_id == year_id)
        if search:
            stmt = stmt.where(ArchiveFolderModel.title.ilike(f"%{search}%"))
        stmt = stmt.order_by(ArchiveFolderModel.index_code)
        result = await self._session.execute(stmt)
        return [(ArchiveFolderMapper.to_domain(m), count) for m, count in result.all()]

    async def save(self, folder: ArchiveFolder) -> ArchiveFolder:
        existing = await self._session.get(
            ArchiveFolderModel, folder.id,
            options=[selectinload(ArchiveFolderModel.retention_period)],
        )
        if existing:
            ArchiveFolderMapper.update_model(existing, folder)
            await self._session.flush()
            await self._session.refresh(existing, attribute_names=["retention_period"])
            return ArchiveFolderMapper.to_domain(existing)
        model = ArchiveFolderMapper.to_model(folder)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["retention_period"])
        return ArchiveFolderMapper.to_domain(model)

    async def delete(self, folder_id: uuid.UUID) -> None:
        model = await self._session.get(ArchiveFolderModel, folder_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

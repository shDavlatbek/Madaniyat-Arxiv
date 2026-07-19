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
            .options(selectinload(ArchiveFolderModel.retention_period), selectinload(ArchiveFolderModel.department))
            .where(ArchiveFolderModel.id == folder_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ArchiveFolderMapper.to_domain(model) if model else None

    async def find_by_index_code(self, index_code: str) -> ArchiveFolder | None:
        stmt = (
            select(ArchiveFolderModel)
            .options(selectinload(ArchiveFolderModel.retention_period), selectinload(ArchiveFolderModel.department))
            .where(ArchiveFolderModel.index_code == index_code)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ArchiveFolderMapper.to_domain(model) if model else None

    async def find_all_with_counts(
        self, search: str | None = None
    ) -> list[tuple[ArchiveFolder, int, int]]:
        # Single round-trip: LEFT JOIN documents, COUNT + SUM(pages), grouped per
        # folder. pages_sum is the automatic total-sheets sum ("avtomatik summa").
        pages_sum = func.coalesce(func.sum(DocumentModel.pages), 0)
        stmt = (
            select(ArchiveFolderModel, func.count(DocumentModel.id), pages_sum)
            .outerjoin(DocumentModel, DocumentModel.archive_folder_id == ArchiveFolderModel.id)
            .options(selectinload(ArchiveFolderModel.retention_period), selectinload(ArchiveFolderModel.department))
            .group_by(ArchiveFolderModel.id)
        )
        if search:
            stmt = stmt.where(ArchiveFolderModel.title.ilike(f"%{search}%"))
        stmt = stmt.order_by(ArchiveFolderModel.index_code)
        result = await self._session.execute(stmt)
        return [
            (ArchiveFolderMapper.to_domain(m), count, int(psum or 0))
            for m, count, psum in result.all()
        ]

    async def save(self, folder: ArchiveFolder) -> ArchiveFolder:
        existing = await self._session.get(ArchiveFolderModel, folder.id)
        if existing:
            ArchiveFolderMapper.update_model(existing, folder)
            await self._session.flush()
            folder_id = existing.id
        else:
            model = ArchiveFolderMapper.to_model(folder)
            self._session.add(model)
            await self._session.flush()
            folder_id = model.id
        # Refetch with relationships eagerly loaded — the mapper denormalizes
        # department + retention_period names and would otherwise trigger
        # implicit lazy loads in the async context.
        saved = await self.find_by_id(folder_id)
        assert saved is not None
        return saved

    async def delete(self, folder_id: uuid.UUID) -> None:
        model = await self._session.get(ArchiveFolderModel, folder_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.music_school_document.entity import MusicSchoolDocument
from src.domain.music_school_document.repository import MusicSchoolDocumentRepository
from src.infrastructure.persistence.mappers.music_school_document_mapper import MusicSchoolDocumentMapper
from src.infrastructure.persistence.models import MusicSchoolDocumentModel, SearchIndexJobModel


class SqlAlchemyMusicSchoolDocumentRepository(MusicSchoolDocumentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, document_id: uuid.UUID) -> MusicSchoolDocument | None:
        stmt = (
            select(MusicSchoolDocumentModel)
            .where(MusicSchoolDocumentModel.id == document_id)
            .options(
                selectinload(MusicSchoolDocumentModel.music_school),
                selectinload(MusicSchoolDocumentModel.specialty)
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return MusicSchoolDocumentMapper.to_domain(model) if model else None

    async def find_all(
        self,
        page: int = 1,
        page_size: int = 20,
        music_school_id: uuid.UUID | None = None,
        graduation_year: int | None = None,
        specialty_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> tuple[list[MusicSchoolDocument], int]:
        stmt = select(MusicSchoolDocumentModel).options(
            selectinload(MusicSchoolDocumentModel.music_school),
            selectinload(MusicSchoolDocumentModel.specialty)
        )
        count_stmt = select(func.count()).select_from(MusicSchoolDocumentModel)

        if music_school_id:
            stmt = stmt.where(MusicSchoolDocumentModel.music_school_id == music_school_id)
            count_stmt = count_stmt.where(MusicSchoolDocumentModel.music_school_id == music_school_id)

        if graduation_year:
            stmt = stmt.where(MusicSchoolDocumentModel.graduation_year == graduation_year)
            count_stmt = count_stmt.where(MusicSchoolDocumentModel.graduation_year == graduation_year)

        if specialty_id:
            stmt = stmt.where(MusicSchoolDocumentModel.specialty_id == specialty_id)
            count_stmt = count_stmt.where(MusicSchoolDocumentModel.specialty_id == specialty_id)

        if search:
            search_filter = or_(
                MusicSchoolDocumentModel.student_full_name.ilike(f"%{search}%"),
                MusicSchoolDocumentModel.diploma_serial.ilike(f"%{search}%"),
                MusicSchoolDocumentModel.diploma_number.ilike(f"%{search}%"),
                MusicSchoolDocumentModel.description.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(MusicSchoolDocumentModel.graduation_year.desc(), MusicSchoolDocumentModel.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [MusicSchoolDocumentMapper.to_domain(m) for m in models], total

    def _enqueue_index_job(self, document_id: uuid.UUID, op: str) -> None:
        """Enqueue outbox indexing job for search worker."""
        self._session.add(SearchIndexJobModel(document_id=document_id, op=op, entity_type="music_school"))

    async def save(self, document: MusicSchoolDocument) -> MusicSchoolDocument:
        existing = await self._session.get(MusicSchoolDocumentModel, document.id)
        if existing:
            MusicSchoolDocumentMapper.update_model(existing, document)
            await self._session.flush()
        else:
            existing = MusicSchoolDocumentMapper.to_model(document)
            self._session.add(existing)
            await self._session.flush()

        stmt = (
            select(MusicSchoolDocumentModel)
            .where(MusicSchoolDocumentModel.id == existing.id)
            .options(
                selectinload(MusicSchoolDocumentModel.music_school),
                selectinload(MusicSchoolDocumentModel.specialty)
            )
        )
        result = await self._session.execute(stmt)
        self._enqueue_index_job(existing.id, "index")
        return MusicSchoolDocumentMapper.to_domain(result.scalar_one())

    async def delete(self, document_id: uuid.UUID) -> None:
        model = await self._session.get(MusicSchoolDocumentModel, document_id)
        if model:
            self._enqueue_index_job(document_id, "delete")
            await self._session.delete(model)
            await self._session.flush()

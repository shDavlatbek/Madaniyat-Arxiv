import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.music_school.entity import MusicSchool
from src.domain.music_school.repository import MusicSchoolRepository
from src.infrastructure.persistence.mappers.music_school_mapper import MusicSchoolMapper
from src.infrastructure.persistence.models import MusicSchoolModel


class SqlAlchemyMusicSchoolRepository(MusicSchoolRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, school_id: uuid.UUID) -> MusicSchool | None:
        model = await self._session.get(MusicSchoolModel, school_id)
        return MusicSchoolMapper.to_domain(model) if model else None

    async def find_by_name(self, name: str) -> MusicSchool | None:
        stmt = select(MusicSchoolModel).where(MusicSchoolModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return MusicSchoolMapper.to_domain(model) if model else None

    async def find_all(self, search: str | None = None) -> list[MusicSchool]:
        stmt = select(MusicSchoolModel)
        if search:
            stmt = stmt.where(MusicSchoolModel.name.ilike(f"%{search}%"))
        stmt = stmt.order_by(MusicSchoolModel.name)
        result = await self._session.execute(stmt)
        return [MusicSchoolMapper.to_domain(m) for m in result.scalars().all()]

    async def save(self, school: MusicSchool) -> MusicSchool:
        existing = await self._session.get(MusicSchoolModel, school.id)
        if existing:
            MusicSchoolMapper.update_model(existing, school)
            await self._session.flush()
            await self._session.refresh(existing)
            return MusicSchoolMapper.to_domain(existing)
        model = MusicSchoolMapper.to_model(school)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return MusicSchoolMapper.to_domain(model)

    async def delete(self, school_id: uuid.UUID) -> None:
        model = await self._session.get(MusicSchoolModel, school_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

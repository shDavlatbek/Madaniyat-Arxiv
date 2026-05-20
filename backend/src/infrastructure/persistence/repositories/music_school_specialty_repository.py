import uuid
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.music_school_specialty.entity import MusicSchoolSpecialty
from src.domain.music_school_specialty.repository import MusicSchoolSpecialtyRepository
from src.infrastructure.persistence.mappers.music_school_specialty_mapper import MusicSchoolSpecialtyMapper
from src.infrastructure.persistence.models import MusicSchoolSpecialtyModel, MusicSchoolDocumentModel


class SqlAlchemyMusicSchoolSpecialtyRepository(MusicSchoolSpecialtyRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, specialty_id: uuid.UUID) -> MusicSchoolSpecialty | None:
        model = await self._session.get(MusicSchoolSpecialtyModel, specialty_id)
        return MusicSchoolSpecialtyMapper.to_domain(model) if model else None

    async def find_all_by_school(self, school_id: uuid.UUID) -> list[MusicSchoolSpecialty]:
        stmt = select(MusicSchoolSpecialtyModel).where(MusicSchoolSpecialtyModel.music_school_id == school_id).order_by(MusicSchoolSpecialtyModel.name)
        result = await self._session.execute(stmt)
        return [MusicSchoolSpecialtyMapper.to_domain(m) for m in result.scalars().all()]

    async def find_by_school_and_name(self, school_id: uuid.UUID, name: str) -> MusicSchoolSpecialty | None:
        stmt = select(MusicSchoolSpecialtyModel).where(
            MusicSchoolSpecialtyModel.music_school_id == school_id,
            MusicSchoolSpecialtyModel.name.ilike(name.strip())
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return MusicSchoolSpecialtyMapper.to_domain(model) if model else None

    async def save(self, specialty: MusicSchoolSpecialty) -> MusicSchoolSpecialty:
        existing = await self._session.get(MusicSchoolSpecialtyModel, specialty.id)
        if existing:
            MusicSchoolSpecialtyMapper.update_model(existing, specialty)
            await self._session.flush()
            await self._session.refresh(existing)
            return MusicSchoolSpecialtyMapper.to_domain(existing)
        model = MusicSchoolSpecialtyMapper.to_model(specialty)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return MusicSchoolSpecialtyMapper.to_domain(model)

    async def delete(self, specialty_id: uuid.UUID) -> None:
        model = await self._session.get(MusicSchoolSpecialtyModel, specialty_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def has_documents_linked(self, specialty_id: uuid.UUID) -> bool:
        stmt = select(exists().where(MusicSchoolDocumentModel.specialty_id == specialty_id))
        result = await self._session.execute(stmt)
        return result.scalar() or False

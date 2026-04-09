import uuid
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.person.entity import Person
from src.domain.person.repository import PersonRepository
from src.infrastructure.persistence.mappers.person_mapper import PersonMapper
from src.infrastructure.persistence.models import PersonModel, PersonTenureModel


class SqlAlchemyPersonRepository(PersonRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, person_id: uuid.UUID) -> Person | None:
        stmt = (
            select(PersonModel)
            .where(PersonModel.id == person_id)
            .options(selectinload(PersonModel.tenures))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return PersonMapper.to_domain(model) if model else None

    async def find_all(self, search: str | None = None) -> list[Person]:
        stmt = select(PersonModel).options(selectinload(PersonModel.tenures))
        if search:
            stmt = stmt.where(PersonModel.full_name.ilike(f"%{search}%"))
        stmt = stmt.order_by(PersonModel.full_name)
        result = await self._session.execute(stmt)
        return [PersonMapper.to_domain(m) for m in result.scalars().unique().all()]

    async def find_active_on_date(self, d: date) -> list[Person]:
        stmt = (
            select(PersonModel)
            .join(PersonTenureModel)
            .where(
                PersonTenureModel.start_date <= d,
                or_(
                    PersonTenureModel.end_date.is_(None),
                    PersonTenureModel.end_date >= d,
                ),
            )
            .options(selectinload(PersonModel.tenures))
            .order_by(PersonModel.full_name)
        )
        result = await self._session.execute(stmt)
        return [PersonMapper.to_domain(m) for m in result.scalars().unique().all()]

    async def save(self, person: Person) -> Person:
        existing = await self._session.get(PersonModel, person.id)
        if existing:
            PersonMapper.update_model(existing, person)
            # Replace tenures
            await self._session.execute(
                PersonTenureModel.__table__.delete().where(
                    PersonTenureModel.person_id == person.id
                )
            )
            await self._session.flush()
            for tenure in person.tenures:
                self._session.add(PersonMapper.tenure_to_model(tenure))
            await self._session.flush()
            stmt = (
                select(PersonModel)
                .where(PersonModel.id == person.id)
                .options(selectinload(PersonModel.tenures))
            )
            result = await self._session.execute(stmt)
            return PersonMapper.to_domain(result.scalar_one())
        else:
            model = PersonMapper.to_model(person)
            self._session.add(model)
            await self._session.flush()
            for tenure in person.tenures:
                tenure.person_id = model.id
                self._session.add(PersonMapper.tenure_to_model(tenure))
            await self._session.flush()
            stmt = (
                select(PersonModel)
                .where(PersonModel.id == model.id)
                .options(selectinload(PersonModel.tenures))
            )
            result = await self._session.execute(stmt)
            return PersonMapper.to_domain(result.scalar_one())

    async def delete(self, person_id: uuid.UUID) -> None:
        model = await self._session.get(PersonModel, person_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

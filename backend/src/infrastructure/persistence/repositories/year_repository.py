from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.year.entity import Year
from src.domain.year.repository import YearRepository
from src.infrastructure.persistence.mappers.year_mapper import YearMapper
from src.infrastructure.persistence.models import YearModel


class SqlAlchemyYearRepository(YearRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self, active_only: bool = True) -> list[Year]:
        stmt = select(YearModel).order_by(YearModel.value.desc())
        if active_only:
            stmt = stmt.where(YearModel.is_active == True)
        result = await self._session.execute(stmt)
        return [YearMapper.to_domain(m) for m in result.scalars().all()]

    async def find_by_id(self, year_id: int) -> Year | None:
        model = await self._session.get(YearModel, year_id)
        return YearMapper.to_domain(model) if model else None

    async def find_by_value(self, value: int) -> Year | None:
        stmt = select(YearModel).where(YearModel.value == value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return YearMapper.to_domain(model) if model else None

    async def save(self, year: Year) -> Year:
        if year.id is not None:
            existing = await self._session.get(YearModel, year.id)
            if existing:
                YearMapper.update_model(existing, year)
                await self._session.flush()
                return YearMapper.to_domain(existing)

        model = YearMapper.to_model(year)
        self._session.add(model)
        await self._session.flush()
        return YearMapper.to_domain(model)

    async def delete(self, year_id: int) -> None:
        model = await self._session.get(YearModel, year_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

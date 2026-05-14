from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import (
    AppealTypeModel,
    ReceptionPlaceModel,
    RegionModel,
)


class SqlAlchemyReferenceRepository:
    """Read-only access to the seed reference tables backing the Murojaat form.

    These tables (regions, reception_places, appeal_types) are immutable seed
    data with no admin CRUD, so they skip the full domain/application layering
    used by editable aggregates — a thin query repository is enough.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_regions(self, region_type: str | None = None) -> list[RegionModel]:
        stmt = select(RegionModel)
        if region_type:
            stmt = stmt.where(RegionModel.type == region_type.strip().upper())
        stmt = stmt.order_by(RegionModel.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_reception_places(self) -> list[ReceptionPlaceModel]:
        stmt = select(ReceptionPlaceModel).order_by(ReceptionPlaceModel.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_appeal_types(self) -> list[AppealTypeModel]:
        stmt = select(AppealTypeModel).order_by(AppealTypeModel.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

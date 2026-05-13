import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.department.entity import Department
from src.domain.department.repository import DepartmentRepository
from src.infrastructure.persistence.mappers.department_mapper import DepartmentMapper
from src.infrastructure.persistence.models import DepartmentModel


class SqlAlchemyDepartmentRepository(DepartmentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, department_id: uuid.UUID) -> Department | None:
        model = await self._session.get(DepartmentModel, department_id)
        return DepartmentMapper.to_domain(model) if model else None

    async def find_by_name(self, name: str) -> Department | None:
        stmt = select(DepartmentModel).where(DepartmentModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DepartmentMapper.to_domain(model) if model else None

    async def find_all(self, search: str | None = None, active_only: bool = False) -> list[Department]:
        stmt = select(DepartmentModel)
        if search:
            stmt = stmt.where(DepartmentModel.name.ilike(f"%{search}%"))
        if active_only:
            stmt = stmt.where(DepartmentModel.is_active.is_(True))
        stmt = stmt.order_by(DepartmentModel.name)
        result = await self._session.execute(stmt)
        return [DepartmentMapper.to_domain(m) for m in result.scalars().all()]

    async def save(self, department: Department) -> Department:
        existing = await self._session.get(DepartmentModel, department.id)
        if existing:
            DepartmentMapper.update_model(existing, department)
            await self._session.flush()
            await self._session.refresh(existing)
            return DepartmentMapper.to_domain(existing)
        model = DepartmentMapper.to_model(department)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return DepartmentMapper.to_domain(model)

    async def delete(self, department_id: uuid.UUID) -> None:
        model = await self._session.get(DepartmentModel, department_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

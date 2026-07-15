from __future__ import annotations

from src.domain.department.entity import Department
from src.domain.department.repository import DepartmentRepository
from src.domain.shared.errors import NotFoundError, ValidationError

from .commands import (
    ActivateDepartmentCommand,
    CreateDepartmentCommand,
    DeactivateDepartmentCommand,
    DeleteDepartmentCommand,
    UpdateDepartmentCommand,
)
from .queries import GetDepartmentQuery, ListDepartmentsQuery


class DepartmentCommandHandler:
    def __init__(self, department_repo: DepartmentRepository):
        self._department_repo = department_repo

    async def create(self, command: CreateDepartmentCommand) -> Department:
        existing = await self._department_repo.find_by_name(command.name.strip())
        if existing:
            raise ValidationError(f"Department '{command.name}' already exists")
        department = Department(
            name=command.name,
            index_code=command.index_code,
            description=command.description,
            year_id=command.year_id,
        )
        return await self._department_repo.save(department)

    async def update(self, command: UpdateDepartmentCommand) -> Department:
        department = await self._department_repo.find_by_id(command.department_id)
        if not department:
            raise NotFoundError("Department", str(command.department_id))
        if command.name is not None and command.name.strip() != department.name:
            clash = await self._department_repo.find_by_name(command.name.strip())
            if clash and clash.id != department.id:
                raise ValidationError(f"Department '{command.name}' already exists")
        department.update(
            name=command.name,
            index_code=command.index_code,
            description=command.description,
            year_id=command.year_id,
        )
        return await self._department_repo.save(department)

    async def delete(self, command: DeleteDepartmentCommand) -> None:
        department = await self._department_repo.find_by_id(command.department_id)
        if not department:
            raise NotFoundError("Department", str(command.department_id))
        await self._department_repo.delete(command.department_id)

    async def activate(self, command: ActivateDepartmentCommand) -> Department:
        department = await self._department_repo.find_by_id(command.department_id)
        if not department:
            raise NotFoundError("Department", str(command.department_id))
        department.activate()
        return await self._department_repo.save(department)

    async def deactivate(self, command: DeactivateDepartmentCommand) -> Department:
        department = await self._department_repo.find_by_id(command.department_id)
        if not department:
            raise NotFoundError("Department", str(command.department_id))
        department.deactivate()
        return await self._department_repo.save(department)


class DepartmentQueryHandler:
    def __init__(self, department_repo: DepartmentRepository):
        self._department_repo = department_repo

    async def list_departments(self, query: ListDepartmentsQuery) -> list[Department]:
        return await self._department_repo.find_all(search=query.search, active_only=query.active_only)

    async def get_department(self, query: GetDepartmentQuery) -> Department:
        department = await self._department_repo.find_by_id(query.department_id)
        if not department:
            raise NotFoundError("Department", str(query.department_id))
        return department

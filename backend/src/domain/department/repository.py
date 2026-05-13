from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.department.entity import Department


class DepartmentRepository(ABC):
    @abstractmethod
    async def find_by_id(self, department_id: uuid.UUID) -> Department | None: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Department | None: ...

    @abstractmethod
    async def find_all(self, search: str | None = None, active_only: bool = False) -> list[Department]: ...

    @abstractmethod
    async def save(self, department: Department) -> Department: ...

    @abstractmethod
    async def delete(self, department_id: uuid.UUID) -> None: ...

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.category.entity import Category, CategoryField


class CategoryRepository(ABC):
    @abstractmethod
    async def find_by_id(self, category_id: uuid.UUID) -> Category | None: ...

    @abstractmethod
    async def find_all(self) -> list[Category]: ...

    @abstractmethod
    async def find_by_year(self, year_id: int) -> list[Category]: ...

    @abstractmethod
    async def save(self, category: Category) -> Category: ...

    @abstractmethod
    async def delete(self, category_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def link_to_year(self, year_id: int, category_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def unlink_from_year(self, year_id: int, category_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def find_field_by_id(self, field_id: uuid.UUID) -> CategoryField | None: ...

    @abstractmethod
    async def find_fields_by_category(self, category_id: uuid.UUID) -> list[CategoryField]: ...

    @abstractmethod
    async def save_field(self, field: CategoryField) -> CategoryField: ...

    @abstractmethod
    async def delete_field(self, field_id: uuid.UUID) -> None: ...

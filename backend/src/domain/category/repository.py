from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.category.entity import Category, CategoryField, DefaultField


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
    async def set_year_links(self, category_id: uuid.UUID, year_ids: list[int]) -> None: ...

    @abstractmethod
    async def copy_category(self, source_id: uuid.UUID, target_year_ids: list[int]) -> Category: ...

    @abstractmethod
    async def find_field_by_id(self, field_id: uuid.UUID) -> CategoryField | None: ...

    @abstractmethod
    async def find_fields_by_category(self, category_id: uuid.UUID) -> list[CategoryField]: ...

    @abstractmethod
    async def save_field(self, field: CategoryField) -> CategoryField: ...

    @abstractmethod
    async def delete_field(self, field_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def find_all_default_fields(self) -> list[DefaultField]: ...

    @abstractmethod
    async def save_default_field(self, field: DefaultField) -> DefaultField: ...

    @abstractmethod
    async def delete_default_field(self, field_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def find_default_field_by_id(self, field_id: uuid.UUID) -> DefaultField | None: ...

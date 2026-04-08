from __future__ import annotations

from src.domain.category.entity import Category, CategoryField
from src.domain.category.repository import CategoryRepository
from src.domain.category.value_objects import FieldType
from src.domain.shared.errors import NotFoundError

from .commands import (
    AddFieldCommand,
    CreateCategoryCommand,
    DeleteCategoryCommand,
    DeleteFieldCommand,
    LinkCategoryToYearCommand,
    UnlinkCategoryFromYearCommand,
    UpdateCategoryCommand,
    UpdateFieldCommand,
)
from .queries import GetCategoryFieldsQuery, ListAllCategoriesQuery, ListCategoriesByYearQuery


class CategoryCommandHandler:
    def __init__(self, category_repo: CategoryRepository):
        self._category_repo = category_repo

    async def create(self, command: CreateCategoryCommand) -> Category:
        category = Category(
            name=command.name,
            code=command.code,
            description=command.description,
            sort_order=command.sort_order,
        )
        return await self._category_repo.save(category)

    async def update(self, command: UpdateCategoryCommand) -> Category:
        category = await self._category_repo.find_by_id(command.category_id)
        if not category:
            raise NotFoundError("Category", str(command.category_id))
        category.update(
            name=command.name,
            code=command.code,
            description=command.description,
            sort_order=command.sort_order,
        )
        return await self._category_repo.save(category)

    async def delete(self, command: DeleteCategoryCommand) -> None:
        await self._category_repo.delete(command.category_id)

    async def add_field(self, command: AddFieldCommand) -> CategoryField:
        field = CategoryField(
            category_id=command.category_id,
            name=command.name,
            label=command.label,
            field_type=FieldType(command.field_type),
            is_required=command.is_required,
            sort_order=command.sort_order,
            options=command.options,
            placeholder=command.placeholder,
            validation=command.validation,
        )
        return await self._category_repo.save_field(field)

    async def update_field(self, command: UpdateFieldCommand) -> CategoryField:
        field = await self._category_repo.find_field_by_id(command.field_id)
        if not field:
            raise NotFoundError("CategoryField", str(command.field_id))
        ft = FieldType(command.field_type) if command.field_type else None
        field.update(
            label=command.label,
            field_type=ft,
            is_required=command.is_required,
            sort_order=command.sort_order,
            options=command.options,
            placeholder=command.placeholder,
            validation=command.validation,
        )
        return await self._category_repo.save_field(field)

    async def delete_field(self, command: DeleteFieldCommand) -> None:
        await self._category_repo.delete_field(command.field_id)

    async def link_to_year(self, command: LinkCategoryToYearCommand) -> None:
        await self._category_repo.link_to_year(command.year_id, command.category_id)

    async def unlink_from_year(self, command: UnlinkCategoryFromYearCommand) -> None:
        await self._category_repo.unlink_from_year(command.year_id, command.category_id)


class CategoryQueryHandler:
    def __init__(self, category_repo: CategoryRepository):
        self._category_repo = category_repo

    async def list_by_year(self, query: ListCategoriesByYearQuery) -> list[Category]:
        return await self._category_repo.find_by_year(query.year_id)

    async def list_all(self, query: ListAllCategoriesQuery) -> list[Category]:
        return await self._category_repo.find_all()

    async def get_fields(self, query: GetCategoryFieldsQuery) -> list[CategoryField]:
        return await self._category_repo.find_fields_by_category(query.category_id)

from __future__ import annotations

from src.domain.category.entity import Category, CategoryField, DefaultField
from src.domain.category.repository import CategoryRepository
from src.domain.category.value_objects import FieldType
from src.domain.shared.errors import NotFoundError

from .commands import (
    AddFieldCommand,
    CopyCategoryCommand,
    CreateCategoryCommand,
    CreateDefaultFieldCommand,
    DeleteCategoryCommand,
    DeleteDefaultFieldCommand,
    DeleteFieldCommand,
    UpdateCategoryCommand,
    UpdateDefaultFieldCommand,
    UpdateFieldCommand,
)
from .queries import GetCategoryFieldsQuery, ListAllCategoriesQuery, ListCategoriesByYearQuery, ListDefaultFieldsQuery


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
        saved = await self._category_repo.save(category)

        # Auto-create fields from default_fields
        default_fields = await self._category_repo.find_all_default_fields()
        for df in default_fields:
            new_field = CategoryField(
                category_id=saved.id,
                name=df.name,
                label=df.label,
                field_type=df.field_type,
                is_required=df.is_required,
                sort_order=df.sort_order,
                options=df.options,
                placeholder=df.placeholder,
            )
            await self._category_repo.save_field(new_field)

        # Set year links
        await self._category_repo.set_year_links(saved.id, command.year_ids)

        # Re-fetch to get fields and year links
        saved = await self._category_repo.find_by_id(saved.id)

        return saved

    async def update(self, command: UpdateCategoryCommand) -> Category:
        category = await self._category_repo.find_by_id(command.category_id)
        if not category:
            raise NotFoundError("Category", str(command.category_id))
        category.update(
            name=command.name,
            code=command.code,
            description=command.description,
            sort_order=command.sort_order,
            year_ids=command.year_ids,
        )
        saved = await self._category_repo.save(category)
        if command.year_ids is not None:
            await self._category_repo.set_year_links(category.id, command.year_ids)
            saved = await self._category_repo.find_by_id(category.id)
        return saved

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

    async def copy_category(self, command: CopyCategoryCommand) -> Category:
        return await self._category_repo.copy_category(
            command.source_category_id, command.target_year_ids,
        )

    async def create_default_field(self, command: CreateDefaultFieldCommand) -> DefaultField:
        field = DefaultField(
            name=command.name,
            label=command.label,
            field_type=FieldType(command.field_type),
            is_required=command.is_required,
            sort_order=command.sort_order,
            options=command.options,
            placeholder=command.placeholder,
        )
        return await self._category_repo.save_default_field(field)

    async def update_default_field(self, command: UpdateDefaultFieldCommand) -> DefaultField:
        field = await self._category_repo.find_default_field_by_id(command.field_id)
        if not field:
            raise NotFoundError("DefaultField", str(command.field_id))
        ft = FieldType(command.field_type) if command.field_type else None
        field.update(
            label=command.label,
            field_type=ft,
            is_required=command.is_required,
            sort_order=command.sort_order,
            options=command.options,
            placeholder=command.placeholder,
        )
        return await self._category_repo.save_default_field(field)

    async def delete_default_field(self, command: DeleteDefaultFieldCommand) -> None:
        await self._category_repo.delete_default_field(command.field_id)


class CategoryQueryHandler:
    def __init__(self, category_repo: CategoryRepository):
        self._category_repo = category_repo

    async def list_by_year(self, query: ListCategoriesByYearQuery) -> list[Category]:
        return await self._category_repo.find_by_year(query.year_id)

    async def list_all(self, query: ListAllCategoriesQuery) -> list[Category]:
        return await self._category_repo.find_all()

    async def get_fields(self, query: GetCategoryFieldsQuery) -> list[CategoryField]:
        return await self._category_repo.find_fields_by_category(query.category_id)

    async def list_default_fields(self, query: ListDefaultFieldsQuery) -> list[DefaultField]:
        return await self._category_repo.find_all_default_fields()

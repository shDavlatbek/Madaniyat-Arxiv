import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.category.entity import Category, CategoryField, DefaultField
from src.domain.category.repository import CategoryRepository
from src.domain.category.value_objects import FieldType
from src.domain.shared.errors import NotFoundError
from src.infrastructure.persistence.mappers.category_mapper import CategoryFieldMapper, CategoryMapper, DefaultFieldMapper
from src.infrastructure.persistence.models import CategoryFieldModel, CategoryModel, DefaultFieldModel, YearModel


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, category_id: uuid.UUID) -> Category | None:
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.id == category_id)
            .options(selectinload(CategoryModel.fields))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return CategoryMapper.to_domain(model) if model else None

    async def find_all(self) -> list[Category]:
        stmt = (
            select(CategoryModel)
            .options(selectinload(CategoryModel.fields))
            .order_by(CategoryModel.sort_order)
        )
        result = await self._session.execute(stmt)
        return [CategoryMapper.to_domain(m) for m in result.scalars().all()]

    async def find_by_year(self, year_id: int) -> list[Category]:
        # year_id param is actually the year VALUE (e.g. 2020), not the DB primary key
        stmt = (
            select(CategoryModel)
            .join(YearModel, YearModel.id == CategoryModel.year_id)
            .where(YearModel.value == year_id)
            .options(selectinload(CategoryModel.fields))
            .order_by(CategoryModel.sort_order)
        )
        result = await self._session.execute(stmt)
        return [CategoryMapper.to_domain(m) for m in result.scalars().all()]

    async def save(self, category: Category) -> Category:
        existing_stmt = (
            select(CategoryModel)
            .where(CategoryModel.id == category.id)
            .options(selectinload(CategoryModel.fields))
        )
        existing_result = await self._session.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()

        if existing:
            CategoryMapper.update_model(existing, category)
            await self._session.flush()
            return CategoryMapper.to_domain(existing)
        else:
            model = CategoryMapper.to_model(category)
            self._session.add(model)
            await self._session.flush()
            # Reload with fields
            stmt = (
                select(CategoryModel)
                .where(CategoryModel.id == model.id)
                .options(selectinload(CategoryModel.fields))
            )
            result = await self._session.execute(stmt)
            return CategoryMapper.to_domain(result.scalar_one())

    async def delete(self, category_id: uuid.UUID) -> None:
        model = await self._session.get(CategoryModel, category_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def copy_category(self, source_id: uuid.UUID, target_year_id: int) -> Category:
        source = await self.find_by_id(source_id)
        if not source:
            raise NotFoundError("Category", str(source_id))
        new_cat = Category(
            name=source.name,
            code=source.code,
            description=source.description,
            sort_order=source.sort_order,
            year_id=target_year_id,
        )
        saved = await self.save(new_cat)
        for field in source.fields:
            new_field = CategoryField(
                category_id=saved.id,
                name=field.name,
                label=field.label,
                field_type=field.field_type,
                is_required=field.is_required,
                sort_order=field.sort_order,
                options=field.options,
                placeholder=field.placeholder,
            )
            await self.save_field(new_field)
        return await self.find_by_id(saved.id)

    async def find_field_by_id(self, field_id: uuid.UUID) -> CategoryField | None:
        model = await self._session.get(CategoryFieldModel, field_id)
        return CategoryFieldMapper.to_domain(model) if model else None

    async def find_fields_by_category(self, category_id: uuid.UUID) -> list[CategoryField]:
        stmt = select(CategoryFieldModel).where(CategoryFieldModel.category_id == category_id).order_by(CategoryFieldModel.sort_order)
        result = await self._session.execute(stmt)
        return [CategoryFieldMapper.to_domain(m) for m in result.scalars().all()]

    async def save_field(self, field: CategoryField) -> CategoryField:
        existing = await self._session.get(CategoryFieldModel, field.id)
        if existing:
            CategoryFieldMapper.update_model(existing, field)
            await self._session.flush()
            return CategoryFieldMapper.to_domain(existing)
        else:
            model = CategoryFieldMapper.to_model(field)
            self._session.add(model)
            await self._session.flush()
            return CategoryFieldMapper.to_domain(model)

    async def delete_field(self, field_id: uuid.UUID) -> None:
        model = await self._session.get(CategoryFieldModel, field_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def find_all_default_fields(self) -> list[DefaultField]:
        stmt = select(DefaultFieldModel).order_by(DefaultFieldModel.sort_order)
        result = await self._session.execute(stmt)
        return [DefaultFieldMapper.to_domain(m) for m in result.scalars().all()]

    async def find_default_field_by_id(self, field_id: uuid.UUID) -> DefaultField | None:
        model = await self._session.get(DefaultFieldModel, field_id)
        return DefaultFieldMapper.to_domain(model) if model else None

    async def save_default_field(self, field: DefaultField) -> DefaultField:
        existing = await self._session.get(DefaultFieldModel, field.id)
        if existing:
            DefaultFieldMapper.update_model(existing, field)
            await self._session.flush()
            return DefaultFieldMapper.to_domain(existing)
        else:
            model = DefaultFieldMapper.to_model(field)
            self._session.add(model)
            await self._session.flush()
            return DefaultFieldMapper.to_domain(model)

    async def delete_default_field(self, field_id: uuid.UUID) -> None:
        model = await self._session.get(DefaultFieldModel, field_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.category.entity import Category, CategoryField
from src.domain.category.repository import CategoryRepository
from src.infrastructure.persistence.mappers.category_mapper import CategoryFieldMapper, CategoryMapper
from src.infrastructure.persistence.models import CategoryFieldModel, CategoryModel, YearCategoryModel


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, category_id: uuid.UUID) -> Category | None:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id).options(selectinload(CategoryModel.fields))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return CategoryMapper.to_domain(model) if model else None

    async def find_all(self) -> list[Category]:
        stmt = select(CategoryModel).options(selectinload(CategoryModel.fields)).order_by(CategoryModel.sort_order)
        result = await self._session.execute(stmt)
        return [CategoryMapper.to_domain(m) for m in result.scalars().all()]

    async def find_by_year(self, year_id: int) -> list[Category]:
        stmt = (
            select(CategoryModel)
            .join(YearCategoryModel, YearCategoryModel.category_id == CategoryModel.id)
            .where(YearCategoryModel.year_id == year_id)
            .options(selectinload(CategoryModel.fields))
            .order_by(CategoryModel.sort_order)
        )
        result = await self._session.execute(stmt)
        return [CategoryMapper.to_domain(m) for m in result.scalars().all()]

    async def save(self, category: Category) -> Category:
        existing_stmt = select(CategoryModel).where(CategoryModel.id == category.id).options(selectinload(CategoryModel.fields))
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
            stmt = select(CategoryModel).where(CategoryModel.id == model.id).options(selectinload(CategoryModel.fields))
            result = await self._session.execute(stmt)
            return CategoryMapper.to_domain(result.scalar_one())

    async def delete(self, category_id: uuid.UUID) -> None:
        model = await self._session.get(CategoryModel, category_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def link_to_year(self, year_id: int, category_id: uuid.UUID) -> None:
        existing = await self._session.execute(
            select(YearCategoryModel).where(
                YearCategoryModel.year_id == year_id,
                YearCategoryModel.category_id == category_id,
            )
        )
        if not existing.scalar_one_or_none():
            link = YearCategoryModel(year_id=year_id, category_id=category_id)
            self._session.add(link)
            await self._session.flush()

    async def unlink_from_year(self, year_id: int, category_id: uuid.UUID) -> None:
        stmt = select(YearCategoryModel).where(
            YearCategoryModel.year_id == year_id,
            YearCategoryModel.category_id == category_id,
        )
        result = await self._session.execute(stmt)
        link = result.scalar_one_or_none()
        if link:
            await self._session.delete(link)
            await self._session.flush()

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

from src.domain.category.entity import Category, CategoryField, DefaultField
from src.domain.category.value_objects import FieldType
from src.infrastructure.persistence.models import CategoryFieldModel, CategoryModel, DefaultFieldModel


class CategoryFieldMapper:
    @staticmethod
    def to_domain(model: CategoryFieldModel) -> CategoryField:
        return CategoryField(
            id=model.id,
            category_id=model.category_id,
            name=model.name,
            label=model.label,
            field_type=FieldType(model.field_type),
            is_required=model.is_required,
            sort_order=model.sort_order,
            options=model.options,
            placeholder=model.placeholder,
            validation=model.validation,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: CategoryField) -> CategoryFieldModel:
        return CategoryFieldModel(
            id=entity.id,
            category_id=entity.category_id,
            name=entity.name,
            label=entity.label,
            field_type=entity.field_type.value,
            is_required=entity.is_required,
            sort_order=entity.sort_order,
            options=entity.options,
            placeholder=entity.placeholder,
            validation=entity.validation,
        )

    @staticmethod
    def update_model(model: CategoryFieldModel, entity: CategoryField) -> None:
        model.label = entity.label
        model.field_type = entity.field_type.value
        model.is_required = entity.is_required
        model.sort_order = entity.sort_order
        model.options = entity.options
        model.placeholder = entity.placeholder
        model.validation = entity.validation


class CategoryMapper:
    @staticmethod
    def to_domain(model: CategoryModel) -> Category:
        fields = [CategoryFieldMapper.to_domain(f) for f in model.fields] if model.fields else []
        year_ids = [yc.year_id for yc in model.year_categories] if model.year_categories else []
        return Category(
            id=model.id,
            name=model.name,
            code=model.code,
            description=model.description,
            sort_order=model.sort_order,
            year_ids=year_ids,
            fields=fields,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Category) -> CategoryModel:
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            description=entity.description,
            sort_order=entity.sort_order,
        )

    @staticmethod
    def update_model(model: CategoryModel, entity: Category) -> None:
        model.name = entity.name
        model.code = entity.code
        model.description = entity.description
        model.sort_order = entity.sort_order


class DefaultFieldMapper:
    @staticmethod
    def to_domain(model: DefaultFieldModel) -> DefaultField:
        return DefaultField(
            id=model.id,
            name=model.name,
            label=model.label,
            field_type=FieldType(model.field_type),
            is_required=model.is_required,
            sort_order=model.sort_order,
            options=model.options,
            placeholder=model.placeholder,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: DefaultField) -> DefaultFieldModel:
        return DefaultFieldModel(
            id=entity.id,
            name=entity.name,
            label=entity.label,
            field_type=entity.field_type.value,
            is_required=entity.is_required,
            sort_order=entity.sort_order,
            options=entity.options,
            placeholder=entity.placeholder,
        )

    @staticmethod
    def update_model(model: DefaultFieldModel, entity: DefaultField) -> None:
        model.label = entity.label
        model.field_type = entity.field_type.value
        model.is_required = entity.is_required
        model.sort_order = entity.sort_order
        model.options = entity.options
        model.placeholder = entity.placeholder

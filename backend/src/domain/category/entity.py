from __future__ import annotations

import uuid
from datetime import datetime, timezone

from src.domain.shared.entity import Entity
from src.domain.category.value_objects import FieldType


class CategoryField(Entity):
    def __init__(
        self,
        category_id: uuid.UUID,
        name: str,
        label: str,
        field_type: FieldType,
        is_required: bool = False,
        sort_order: int = 0,
        options: list[str] | None = None,
        placeholder: str | None = None,
        validation: dict | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.category_id = category_id
        self.name = name
        self.label = label
        self.field_type = field_type
        self.is_required = is_required
        self.sort_order = sort_order
        self.options = options
        self.placeholder = placeholder
        self.validation = validation

    def update(self, label: str | None = None, field_type: FieldType | None = None,
               is_required: bool | None = None, sort_order: int | None = None,
               options: list[str] | None = None, placeholder: str | None = None,
               validation: dict | None = None) -> None:
        if label is not None:
            self.label = label
        if field_type is not None:
            self.field_type = field_type
        if is_required is not None:
            self.is_required = is_required
        if sort_order is not None:
            self.sort_order = sort_order
        if options is not None:
            self.options = options
        if placeholder is not None:
            self.placeholder = placeholder
        if validation is not None:
            self.validation = validation


class DefaultField(Entity):
    def __init__(
        self,
        name: str,
        label: str,
        field_type: FieldType,
        is_required: bool = False,
        sort_order: int = 0,
        options: list[str] | None = None,
        placeholder: str | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.name = name
        self.label = label
        self.field_type = field_type
        self.is_required = is_required
        self.sort_order = sort_order
        self.options = options
        self.placeholder = placeholder

    def update(self, label: str | None = None, field_type: FieldType | None = None,
               is_required: bool | None = None, sort_order: int | None = None,
               options: list[str] | None = None, placeholder: str | None = None) -> None:
        if label is not None:
            self.label = label
        if field_type is not None:
            self.field_type = field_type
        if is_required is not None:
            self.is_required = is_required
        if sort_order is not None:
            self.sort_order = sort_order
        if options is not None:
            self.options = options
        if placeholder is not None:
            self.placeholder = placeholder


class Category(Entity):
    def __init__(
        self,
        name: str,
        code: str,
        description: str | None = None,
        sort_order: int = 0,
        fields: list[CategoryField] | None = None,
        year_id: int | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.name = name
        self.code = code
        self.description = description
        self.sort_order = sort_order
        self.fields = fields or []
        self.year_id = year_id

    def update(self, name: str | None = None, code: str | None = None,
               description: str | None = None, sort_order: int | None = None,
               year_id: int | None = None) -> None:
        if name is not None:
            self.name = name
        if code is not None:
            self.code = code
        if description is not None:
            self.description = description
        if sort_order is not None:
            self.sort_order = sort_order
        if year_id is not None:
            self.year_id = year_id
        self.updated_at = datetime.now(timezone.utc)

    def add_field(self, field: CategoryField) -> None:
        self.fields.append(field)

    def remove_field(self, field_id: uuid.UUID) -> None:
        self.fields = [f for f in self.fields if f.id != field_id]

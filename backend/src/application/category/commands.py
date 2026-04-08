from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class CreateCategoryCommand:
    name: str
    code: str
    year_ids: list[int]
    description: str | None = None
    sort_order: int = 0


@dataclass
class UpdateCategoryCommand:
    category_id: uuid.UUID
    name: str | None = None
    code: str | None = None
    description: str | None = None
    sort_order: int | None = None
    year_ids: list[int] | None = None


@dataclass
class DeleteCategoryCommand:
    category_id: uuid.UUID


@dataclass
class AddFieldCommand:
    category_id: uuid.UUID
    name: str
    label: str
    field_type: str
    is_required: bool = False
    sort_order: int = 0
    options: list[str] | None = None
    placeholder: str | None = None
    validation: dict | None = None


@dataclass
class UpdateFieldCommand:
    field_id: uuid.UUID
    label: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    sort_order: int | None = None
    options: list[str] | None = None
    placeholder: str | None = None
    validation: dict | None = None


@dataclass
class DeleteFieldCommand:
    field_id: uuid.UUID


@dataclass
class CopyCategoryCommand:
    source_category_id: uuid.UUID
    target_year_ids: list[int]


@dataclass
class CreateDefaultFieldCommand:
    name: str
    label: str
    field_type: str
    is_required: bool = False
    sort_order: int = 0
    options: list[str] | None = None
    placeholder: str | None = None


@dataclass
class UpdateDefaultFieldCommand:
    field_id: uuid.UUID
    label: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    sort_order: int | None = None
    options: list[str] | None = None
    placeholder: str | None = None


@dataclass
class DeleteDefaultFieldCommand:
    field_id: uuid.UUID

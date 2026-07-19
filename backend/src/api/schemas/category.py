import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _validate_year_name(v: str | None) -> str | None:
    """A nomenklatura is a 4-digit year number (e.g. "2024")."""
    if v is None:
        return v
    v = v.strip()
    if not (v.isdigit() and len(v) == 4 and 1900 <= int(v) <= 2100):
        raise ValueError("Nomenklatura yil raqami bo'lishi kerak (masalan: 2024)")
    return v


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sort_order: int = 0

    _check_year = field_validator("name")(_validate_year_name)


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    sort_order: int | None = None

    _check_year = field_validator("name")(_validate_year_name)


class AddFieldRequest(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    field_type: str
    is_required: bool = False
    sort_order: int = 0
    options: list[str] | None = None
    placeholder: str | None = None
    validation: dict | None = None


class UpdateFieldRequest(BaseModel):
    label: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    sort_order: int | None = None
    options: list[str] | None = None
    placeholder: str | None = None
    validation: dict | None = None


class CategoryFieldResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    label: str
    field_type: str
    is_required: bool
    sort_order: int
    options: list[str] | None
    placeholder: str | None
    validation: dict | None
    created_at: datetime


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    sort_order: int
    fields: list[CategoryFieldResponse]
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]


class DefaultFieldResponse(BaseModel):
    id: uuid.UUID
    name: str
    label: str
    field_type: str
    is_required: bool
    sort_order: int
    options: list[str] | None
    placeholder: str | None
    created_at: datetime


class CreateDefaultFieldRequest(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    field_type: str
    is_required: bool = False
    sort_order: int = 0
    options: list[str] | None = None
    placeholder: str | None = None


class UpdateDefaultFieldRequest(BaseModel):
    label: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    sort_order: int | None = None
    options: list[str] | None = None
    placeholder: str | None = None


class DefaultFieldListResponse(BaseModel):
    items: list[DefaultFieldResponse]

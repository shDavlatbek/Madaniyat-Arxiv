import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    year_ids: list[int]
    description: str | None = None
    sort_order: int = 0


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    sort_order: int | None = None
    year_ids: list[int] | None = None


class AddFieldRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
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
    year_ids: list[int]
    fields: list[CategoryFieldResponse]
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]


class CopyCategoryRequest(BaseModel):
    target_year_ids: list[int]


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
    name: str = Field(min_length=1, max_length=100)
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

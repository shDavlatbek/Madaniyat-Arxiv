import datetime as dt
import uuid

from pydantic import BaseModel, Field


class CreateDepartmentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    index_code: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=10000)
    year_id: int | None = None


class UpdateDepartmentRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    index_code: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=10000)
    year_id: int | None = None


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    index_code: str | None
    description: str | None
    is_active: bool
    year_id: int | None
    year_value: int | None
    created_at: dt.datetime
    updated_at: dt.datetime


class DepartmentListResponse(BaseModel):
    items: list[DepartmentResponse]

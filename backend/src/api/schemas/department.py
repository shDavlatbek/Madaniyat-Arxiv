import datetime as dt
import uuid

from pydantic import BaseModel, Field


class CreateDepartmentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)


class UpdateDepartmentRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime


class DepartmentListResponse(BaseModel):
    items: list[DepartmentResponse]

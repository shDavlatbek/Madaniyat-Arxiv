from datetime import datetime

from pydantic import BaseModel, Field


class CreateYearRequest(BaseModel):
    value: int = Field(ge=1900, le=2100)
    is_active: bool = True
    import_from_year_id: int | None = None


class UpdateYearRequest(BaseModel):
    value: int | None = Field(default=None, ge=1900, le=2100)
    is_active: bool | None = None


class YearResponse(BaseModel):
    id: int
    value: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class YearListResponse(BaseModel):
    items: list[YearResponse]

import uuid
import datetime as dt

from pydantic import BaseModel, Field


class TenureRequest(BaseModel):
    position: str = Field(min_length=1, max_length=255)
    start_date: dt.date
    end_date: dt.date | None = None


class CreatePersonRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    tenures: list[TenureRequest] = Field(default_factory=list)


class UpdatePersonRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    tenures: list[TenureRequest] | None = None


class TenureResponse(BaseModel):
    id: uuid.UUID
    position: str
    start_date: dt.date
    end_date: dt.date | None
    created_at: dt.datetime


class PersonResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    tenures: list[TenureResponse]
    created_at: dt.datetime
    updated_at: dt.datetime


class PersonListResponse(BaseModel):
    items: list[PersonResponse]

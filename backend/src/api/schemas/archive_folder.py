import datetime as dt
import uuid

from pydantic import BaseModel, Field


class CreateArchiveFolderRequest(BaseModel):
    index_code: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=500)
    start_date: dt.date
    retention_period_id: uuid.UUID | None = None
    end_date: dt.date | None = None
    year_id: int | None = None


class UpdateArchiveFolderRequest(BaseModel):
    index_code: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=500)
    retention_period_id: uuid.UUID | None = None
    start_date: dt.date | None = None
    end_date: dt.date | None = None
    year_id: int | None = None


class ArchiveFolderResponse(BaseModel):
    id: uuid.UUID
    index_code: str
    title: str
    retention_period_id: uuid.UUID | None
    retention_period_name: str | None
    start_date: dt.date
    end_date: dt.date | None
    year_id: int | None
    document_count: int
    created_at: dt.datetime
    updated_at: dt.datetime


class ArchiveFolderListResponse(BaseModel):
    items: list[ArchiveFolderResponse]

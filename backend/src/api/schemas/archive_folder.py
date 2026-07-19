import datetime as dt
import uuid

from pydantic import BaseModel, Field


class CreateArchiveFolderRequest(BaseModel):
    index_code: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=500)
    department_id: uuid.UUID | None = None
    article_number: str | None = Field(default=None, max_length=100)
    list_number: str | None = Field(default=None, max_length=100)
    note: str | None = None
    retention_period_id: uuid.UUID | None = None
    total_sheets: int | None = Field(default=None, ge=0)
    start_date: dt.date | None = None
    end_date: dt.date | None = None


class UpdateArchiveFolderRequest(BaseModel):
    index_code: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=500)
    department_id: uuid.UUID | None = None
    article_number: str | None = Field(default=None, max_length=100)
    list_number: str | None = Field(default=None, max_length=100)
    note: str | None = None
    retention_period_id: uuid.UUID | None = None
    total_sheets: int | None = Field(default=None, ge=0)
    start_date: dt.date | None = None
    end_date: dt.date | None = None


class ArchiveFolderResponse(BaseModel):
    id: uuid.UUID
    index_code: str
    title: str
    department_id: uuid.UUID | None
    department_name: str | None
    department_index_code: str | None
    article_number: str | None
    list_number: str | None
    note: str | None
    retention_period_id: uuid.UUID | None
    retention_period_name: str | None
    total_sheets: int | None
    documents_pages_sum: int
    start_date: dt.date | None
    end_date: dt.date | None
    document_count: int
    created_at: dt.datetime
    updated_at: dt.datetime


class ArchiveFolderListResponse(BaseModel):
    items: list[ArchiveFolderResponse]

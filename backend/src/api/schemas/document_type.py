import datetime as dt
import uuid

from pydantic import BaseModel, Field


class CreateDocumentTypeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=500)


class UpdateDocumentTypeRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=500)


class DocumentTypeResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: dt.datetime
    updated_at: dt.datetime


class DocumentTypeListResponse(BaseModel):
    items: list[DocumentTypeResponse]

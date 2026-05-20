import datetime as dt
import uuid

from pydantic import BaseModel, Field


class MusicSchoolSpecialtyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class MusicSchoolSpecialtyResponse(BaseModel):
    id: uuid.UUID
    music_school_id: uuid.UUID
    name: str
    created_at: dt.datetime
    updated_at: dt.datetime


class MusicSchoolSpecialtyImportRequest(BaseModel):
    source_school_id: uuid.UUID
    specialty_ids: list[uuid.UUID]


class CreateMusicSchoolDocumentRequest(BaseModel):
    student_full_name: str = Field(min_length=1, max_length=255)
    music_school_id: uuid.UUID
    specialty_id: uuid.UUID
    graduation_year: int = Field(gt=1900, lt=2100)
    diploma_serial: str = Field(min_length=1, max_length=50)
    diploma_number: str = Field(min_length=1, max_length=50)
    given_date: dt.date
    description: str | None = None


class UpdateMusicSchoolDocumentRequest(BaseModel):
    student_full_name: str | None = Field(default=None, min_length=1, max_length=255)
    music_school_id: uuid.UUID | None = None
    specialty_id: uuid.UUID | None = None
    graduation_year: int | None = Field(default=None, gt=1900, lt=2100)
    diploma_serial: str | None = Field(default=None, min_length=1, max_length=50)
    diploma_number: str | None = Field(default=None, min_length=1, max_length=50)
    given_date: dt.date | None = None
    description: str | None = None


class MusicSchoolDocumentResponse(BaseModel):
    id: uuid.UUID
    student_full_name: str
    music_school_id: uuid.UUID
    music_school_name: str | None
    specialty_id: uuid.UUID
    specialty: str | None
    graduation_year: int
    diploma_serial: str
    diploma_number: str
    given_date: dt.date
    description: str | None
    file_path: str | None
    ocr_status: str
    ocr_completed_at: dt.datetime | None
    created_by: uuid.UUID | None
    created_at: dt.datetime
    updated_at: dt.datetime


class MusicSchoolDocumentListResponse(BaseModel):
    items: list[MusicSchoolDocumentResponse]
    total: int
    page: int
    page_size: int


from typing import Literal
from src.api.schemas.search import FacetBucket

class MusicSchoolSearchFilters(BaseModel):
    music_school_id: list[uuid.UUID] | None = None
    graduation_year: list[int] | None = None
    specialty: list[str] | None = None
    date_from: dt.date | None = None
    date_to: dt.date | None = None


class MusicSchoolSearchRequest(BaseModel):
    q: str | None = None
    filters: MusicSchoolSearchFilters = Field(default_factory=MusicSchoolSearchFilters)
    facets: list[str] = Field(default_factory=list)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort: Literal["relevance", "date_desc", "date_asc"] = "relevance"


class MusicSchoolSearchHighlight(BaseModel):
    student_full_name: list[str] | None = None
    specialty: list[str] | None = None
    description: list[str] | None = None
    extracted_text: list[str] | None = None


class MusicSchoolSearchHit(BaseModel):
    id: uuid.UUID
    score: float | None = None
    student_full_name: str | None = None
    music_school_id: uuid.UUID | None = None
    music_school_name: str | None = None
    specialty_id: uuid.UUID | None = None
    specialty: str | None = None
    graduation_year: int | None = None
    diploma_serial: str | None = None
    diploma_number: str | None = None
    given_date: dt.date | None = None
    description: str | None = None
    file_path: str | None = None
    ocr_status: str | None = None
    highlights: MusicSchoolSearchHighlight = Field(default_factory=MusicSchoolSearchHighlight)


class MusicSchoolSearchResponse(BaseModel):
    items: list[MusicSchoolSearchHit]
    total: int
    page: int
    page_size: int
    took_ms: int
    facets: dict[str, list[FacetBucket]] = Field(default_factory=dict)


import datetime as dt
import uuid

from pydantic import BaseModel, Field


class CreateMusicSchoolRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=50)
    region: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)


class UpdateMusicSchoolRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=50)
    region: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)


class MusicSchoolResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str | None
    region: str | None
    district: str | None
    created_at: dt.datetime
    updated_at: dt.datetime


class MusicSchoolListResponse(BaseModel):
    items: list[MusicSchoolResponse]

"""Pydantic schemas for the advanced search endpoint."""
from __future__ import annotations

import datetime as dt
import uuid
from typing import Literal

from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    category_id: list[uuid.UUID] | None = None
    document_view: list[str] | None = None
    document_type_id: list[uuid.UUID] | None = None
    archive_folder_id: list[uuid.UUID] | None = None
    person_id: list[uuid.UUID] | None = None
    date_from: dt.date | None = None
    date_to: dt.date | None = None


class SearchRequest(BaseModel):
    q: str | None = None
    filters: SearchFilters = Field(default_factory=SearchFilters)
    facets: list[str] = Field(default_factory=list)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort: Literal["relevance", "date_desc", "date_asc"] = "relevance"


class SearchHighlight(BaseModel):
    """Per-field highlight snippets. Values contain ``<mark>`` HTML the FE
    renders via ``v-html`` — see Plan v2 §Risks for why that's safe."""

    title: list[str] | None = None
    short_desc: list[str] | None = None
    extracted_text: list[str] | None = None
    signer: list[str] | None = None
    person_name: list[str] | None = None
    note: list[str] | None = None
    attachments: list[str] | None = None  # flattened from nested inner_hits


class SearchHit(BaseModel):
    id: uuid.UUID
    score: float | None = None
    title: str | None = None
    document_number: str | None = None
    short_desc: str | None = None
    signer: str | None = None
    archive_number: str | None = None
    date: dt.date | None = None
    category_id: uuid.UUID | None = None
    category_name: str | None = None
    person_id: uuid.UUID | None = None
    person_name: str | None = None
    archive_folder_id: uuid.UUID | None = None
    archive_folder_title: str | None = None
    document_type_id: uuid.UUID | None = None
    document_type_name: str | None = None
    document_view: str | None = None
    highlights: SearchHighlight = Field(default_factory=SearchHighlight)


class FacetBucket(BaseModel):
    value: str
    count: int


class SearchResponse(BaseModel):
    items: list[SearchHit]
    total: int
    page: int
    page_size: int
    took_ms: int
    facets: dict[str, list[FacetBucket]] = Field(default_factory=dict)

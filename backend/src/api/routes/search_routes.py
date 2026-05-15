"""POST /api/search — Elasticsearch-backed full-text + faceted search."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from elasticsearch import AsyncElasticsearch

from src.api.middleware.auth import get_current_user
from src.api.schemas.search import (
    FacetBucket,
    SearchHighlight,
    SearchHit,
    SearchRequest,
    SearchResponse,
)
from src.domain.user.entity import User
from src.infrastructure.search.es_client import get_es
from src.infrastructure.search.index_template import ALIAS
from src.infrastructure.search.query_builder import build_query

router = APIRouter(prefix="/api/search", tags=["search"])


def _es_dep() -> AsyncElasticsearch:
    return get_es()


def _flatten_attachment_highlights(hit: dict) -> list[str]:
    """Pull ``attachments.extracted_text`` snippets out of the nested
    ``inner_hits`` block so the FE doesn't have to walk that structure."""
    out: list[str] = []
    inner = hit.get("inner_hits", {}).get("attachments", {})
    for nested_hit in inner.get("hits", {}).get("hits", []):
        snippets = nested_hit.get("highlight", {}).get("attachments.extracted_text", [])
        out.extend(snippets)
    return out


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    es: AsyncElasticsearch = Depends(_es_dep),
    _: User = Depends(get_current_user),
) -> SearchResponse:
    body = build_query(
        q=request.q,
        filters=request.filters.model_dump(mode="json", exclude_none=True),
        facets=request.facets,
        page=request.page,
        page_size=request.page_size,
        sort=request.sort,
    )

    raw = await es.search(index=ALIAS, body=body)

    items: list[SearchHit] = []
    for hit in raw["hits"]["hits"]:
        src = hit["_source"]
        hl = hit.get("highlight", {})
        items.append(SearchHit(
            id=src["id"],
            score=hit.get("_score"),
            title=src.get("title"),
            document_number=src.get("document_number"),
            short_desc=src.get("short_desc"),
            signer=src.get("signer"),
            archive_number=src.get("archive_number"),
            date=src.get("date"),
            year_id=src.get("year_id"),
            year_value=src.get("year_value"),
            category_id=src.get("category_id"),
            category_name=src.get("category_name"),
            person_id=src.get("person_id"),
            person_name=src.get("person_name"),
            archive_folder_id=src.get("archive_folder_id"),
            archive_folder_title=src.get("archive_folder_title"),
            document_type_id=src.get("document_type_id"),
            document_type_name=src.get("document_type_name"),
            document_view=src.get("document_view"),
            highlights=SearchHighlight(
                title=hl.get("title"),
                short_desc=hl.get("short_desc"),
                extracted_text=hl.get("extracted_text"),
                signer=hl.get("signer"),
                person_name=hl.get("person_name"),
                note=hl.get("note"),
                attachments=_flatten_attachment_highlights(hit) or None,
            ),
        ))

    facets: dict[str, list[FacetBucket]] = {}
    for agg_name, agg in raw.get("aggregations", {}).items():
        facets[agg_name] = [
            FacetBucket(value=str(b["key"]), count=b["doc_count"])
            for b in agg.get("buckets", [])
        ]

    return SearchResponse(
        items=items,
        total=raw["hits"]["total"]["value"],
        page=request.page,
        page_size=request.page_size,
        took_ms=raw["took"],
        facets=facets,
    )

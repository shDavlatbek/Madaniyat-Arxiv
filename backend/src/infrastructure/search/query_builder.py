"""Translate a :class:`SearchRequest` into an Elasticsearch query body.

Kept separate from the route handler so the shape is unit-testable and
reusable (e.g. by a future export endpoint that hits the same engine
without going through Pydantic validation again).

Conventions:
  * Free text → ``multi_match`` (best_fields, cross_fields-like via boosts)
    over title^3, document_number^3, short_desc^2, signer, person_name,
    extracted_text, plus a ``nested`` clause against
    attachments.extracted_text.
  * Filters → ``bool.filter`` (constant-score; no relevance boost).
  * Date range → single ``range`` clause on ``date``.
  * Facets → terms aggregations on the requested keyword fields.
  * Highlights → fragment_size=150, number_of_fragments=3, ``<mark>`` tags.
"""
from __future__ import annotations

from typing import Any

# Field weights — bumped up for fields a user expects to match strongest.
_MATCH_FIELDS = [
    "title^3",
    "document_number^3",
    "short_desc^2",
    "signer",
    "person_name",
    "archive_number",
    "extracted_text",
    "note",
]

_KEYWORD_FILTER_FIELDS = {
    "category_id",
    "document_view",
    "document_type_id",
    "archive_folder_id",
    "person_id",
}


def build_query(
    *,
    q: str | None,
    filters: dict[str, Any],
    facets: list[str],
    page: int,
    page_size: int,
    sort: str,
) -> dict[str, Any]:
    """Return the raw ES request body."""
    must: list[dict] = []
    if q:
        # Nested attachment text can't live inside multi_match, so the two
        # candidates (main fields, nested attachments) sit under a single
        # bool.should with minimum_should_match=1: a hit on either side
        # qualifies the document.
        must.append({
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": q,
                            "fields": _MATCH_FIELDS,
                            "type": "best_fields",
                            "operator": "or",
                        }
                    },
                    {
                        "nested": {
                            "path": "attachments",
                            "query": {"match": {"attachments.extracted_text": q}},
                            "inner_hits": {
                                "size": 3,
                                "highlight": {
                                    "pre_tags": ["<mark>"],
                                    "post_tags": ["</mark>"],
                                    "fragment_size": 150,
                                    "number_of_fragments": 2,
                                    "fields": {"attachments.extracted_text": {}},
                                },
                            },
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        })

    filter_clauses: list[dict] = []
    for field in _KEYWORD_FILTER_FIELDS:
        values = filters.get(field)
        if values:
            filter_clauses.append({"terms": {field: values}})

    if filters.get("date_from") or filters.get("date_to"):
        rng: dict[str, str] = {}
        if filters.get("date_from"):
            rng["gte"] = filters["date_from"]
        if filters.get("date_to"):
            rng["lte"] = filters["date_to"]
        filter_clauses.append({"range": {"date": rng}})

    body: dict[str, Any] = {
        "from": max(0, (page - 1) * page_size),
        "size": page_size,
        "track_total_hits": True,
        "query": {
            "bool": {
                "must": must or [{"match_all": {}}],
                "filter": filter_clauses,
            }
        },
        "highlight": {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fragment_size": 150,
            "number_of_fragments": 3,
            "fields": {
                "title": {"number_of_fragments": 0},
                "short_desc": {},
                "extracted_text": {},
                "signer": {"number_of_fragments": 0},
                "person_name": {"number_of_fragments": 0},
                "note": {},
            },
        },
    }

    if sort == "date_desc":
        body["sort"] = [{"date": "desc"}]
    elif sort == "date_asc":
        body["sort"] = [{"date": "asc"}]
    # "relevance" leaves ES's default _score sort in place.

    # Facets — terms aggregation per requested keyword field. Date / id
    # fields keep their natural keyword type so counts come back as-is.
    if facets:
        body["aggs"] = {
            field: {"terms": {"field": field, "size": 50}}
            for field in facets
            if field in _KEYWORD_FILTER_FIELDS
        }

    return body

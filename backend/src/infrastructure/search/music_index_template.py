"""Elasticsearch index definition for the ``music_documents`` alias.

Index naming follows the versioned-alias pattern so we can reindex without
downtime. Reads + writes always go through the ``music_documents`` alias; the alias
points at one concrete index (``music_documents-v1``).
"""
from __future__ import annotations

import logging

from elasticsearch import AsyncElasticsearch, NotFoundError
from src.infrastructure.search.index_template import ANALYSIS_SETTINGS

log = logging.getLogger("search.music_index_template")

ALIAS = "music_documents"
INDEX_V1 = "music_documents-v1"

_TEXT = {"type": "text", "analyzer": "uz_multi"}
_TEXT_WITH_KEYWORD = {
    "type": "text",
    "analyzer": "uz_multi",
    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
}
_KEYWORD = {"type": "keyword"}
_DATE = {"type": "date"}
_LONG = {"type": "long"}

MAPPING = {
    "properties": {
        "id": _KEYWORD,
        "student_full_name": {
            "type": "text",
            "analyzer": "uz_multi",
            "fields": {
                "autocomplete": {"type": "text", "analyzer": "uz_autocomplete", "search_analyzer": "uz_multi"},
                "keyword": {"type": "keyword", "ignore_above": 512},
            },
        },
        "music_school_id": _KEYWORD,
        "music_school_name": _TEXT_WITH_KEYWORD,
        "specialty_id": _KEYWORD,
        "specialty": _TEXT_WITH_KEYWORD,
        "graduation_year": _LONG,
        "diploma_serial": _KEYWORD,
        "diploma_number": _KEYWORD,
        "given_date": _DATE,
        "description": _TEXT,
        "file_path": _TEXT,
        "extracted_text": _TEXT,
        "ocr_status": _KEYWORD,
        "created_by": _KEYWORD,
        "created_at": _DATE,
        "updated_at": _DATE,
    },
}

INDEX_BODY = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": ANALYSIS_SETTINGS,
    },
    "mappings": MAPPING,
}


async def ensure_index(es: AsyncElasticsearch) -> None:
    """Idempotent: create ``music_documents-v1`` if missing and bind the ``music_documents`` alias."""
    if not await es.indices.exists(index=INDEX_V1):
        log.info("Creating ES index %s", INDEX_V1)
        await es.indices.create(index=INDEX_V1, body=INDEX_BODY)
    else:
        log.debug("ES index %s already exists", INDEX_V1)

    # Make sure the alias points at the current concrete index.
    try:
        existing = await es.indices.get_alias(name=ALIAS)
        already_bound = INDEX_V1 in existing
    except NotFoundError:
        already_bound = False

    if not already_bound:
        log.info("Pointing ES alias %s -> %s", ALIAS, INDEX_V1)
        await es.indices.put_alias(index=INDEX_V1, name=ALIAS)

"""Elasticsearch index definition for the ``documents`` alias.

Index naming follows the **versioned-alias** pattern so we can reindex without
downtime. Reads + writes always go through the ``documents`` alias; the alias
points at one concrete index (``documents-v1`` today). When a mapping change
needs a reindex, we build ``documents-v2``, populate it, then atomically swap
the alias.

Phase 5 ships v1 — Phase 6 will populate the OCR text fields that are already
defined here but empty until then.
"""
from __future__ import annotations

import logging

from elasticsearch import AsyncElasticsearch, NotFoundError

log = logging.getLogger("search.index_template")

ALIAS = "documents"
INDEX_V1 = "documents-v1"


# ---------------------------------------------------------------------------
# Analyzers
# ---------------------------------------------------------------------------
# Uzbek archive content mixes Latin Uzbek, Cyrillic Uzbek, and Russian. The
# ICU tokenizer + folding handles all three scripts; the Russian stemmer
# improves recall on Russian-language documents (which are common in the
# corpus). For autocomplete on titles we layer an edge-ngram on top.

ANALYSIS_SETTINGS = {
    "filter": {
        "russian_stemmer": {
            "type": "stemmer",
            "language": "russian",
        },
        "edge_ngram_2_10": {
            "type": "edge_ngram",
            "min_gram": 2,
            "max_gram": 10,
        },
    },
    "analyzer": {
        "uz_multi": {
            "type": "custom",
            "tokenizer": "icu_tokenizer",
            "filter": ["lowercase", "icu_folding", "russian_stemmer"],
        },
        "uz_autocomplete": {
            "type": "custom",
            "tokenizer": "icu_tokenizer",
            "filter": [
                "lowercase",
                "icu_folding",
                "russian_stemmer",
                "edge_ngram_2_10",
            ],
        },
    },
}


# ---------------------------------------------------------------------------
# Mapping
# ---------------------------------------------------------------------------
# Convention:
#   * IDs (UUIDs) and short codes → keyword (exact-match + aggregations)
#   * Free text → text with ``uz_multi`` analyzer
#   * Titles also indexed with ``uz_autocomplete`` for prefix search
#   * Dates → date
#   * Numeric fields (e.g. pages) → long

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
        # ─── denormalized refs ──────────────────────────────────────────
        "category_id": _KEYWORD,
        "category_name": _TEXT_WITH_KEYWORD,
        "person_id": _KEYWORD,
        "person_name": _TEXT_WITH_KEYWORD,
        "person_position": _TEXT,
        "archive_folder_id": _KEYWORD,
        "archive_folder_index_code": _KEYWORD,
        "archive_folder_title": _TEXT_WITH_KEYWORD,
        "document_type_id": _KEYWORD,
        "document_type_name": _TEXT_WITH_KEYWORD,
        # ─── core document fields ───────────────────────────────────────
        "title": {
            "type": "text",
            "analyzer": "uz_multi",
            "fields": {
                "autocomplete": {"type": "text", "analyzer": "uz_autocomplete", "search_analyzer": "uz_multi"},
                "keyword": {"type": "keyword", "ignore_above": 512},
            },
        },
        "document_number": {
            "type": "text",
            "analyzer": "uz_multi",
            "fields": {"keyword": {"type": "keyword", "ignore_above": 128}},
        },
        "short_desc": _TEXT,
        "signer": _TEXT_WITH_KEYWORD,
        "signed_by": _TEXT_WITH_KEYWORD,
        "archive_number": _KEYWORD,
        "document_view": _KEYWORD,
        "document_form": _TEXT_WITH_KEYWORD,
        "sender": _TEXT_WITH_KEYWORD,
        "language": _KEYWORD,
        "related_document_number": _KEYWORD,
        "related_document_date": _DATE,
        "received_date": _DATE,
        "origin_organization": _TEXT_WITH_KEYWORD,
        "sent_date": _DATE,
        "recipient_organization": _TEXT_WITH_KEYWORD,
        "applicant_full_name": _TEXT_WITH_KEYWORD,
        "applicant_phone": _KEYWORD,
        "person_type": _KEYWORD,
        "outgoing_number": _KEYWORD,
        "outgoing_date": _DATE,
        "note": _TEXT,
        "pages": _LONG,
        "date": _DATE,
        "created_at": _DATE,
        "updated_at": _DATE,
        # ─── full-text (populated by Phase 6 OCR pipeline) ─────────────
        "extracted_text": _TEXT,
        "ocr_status": _KEYWORD,
        # ─── nested children ────────────────────────────────────────────
        "attachments": {
            "type": "nested",
            "properties": {
                "id": _KEYWORD,
                "original_filename": _TEXT_WITH_KEYWORD,
                "extracted_text": _TEXT,
                "ocr_status": _KEYWORD,
            },
        },
        "field_values": {
            "type": "nested",
            "properties": {
                "name": _KEYWORD,
                "label": _KEYWORD,
                "value": _TEXT,
            },
        },
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
    """Idempotent: create ``documents-v1`` if missing and bind the ``documents`` alias.

    Safe to call on every app startup. No-op when the index + alias already
    exist with the expected configuration.
    """
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

"""Indexer service: Postgres ``music_school_documents`` row → Elasticsearch ``music_documents`` alias.

Reads one music school document at a time with its denormalized school ref
and writes a single ES document. The mapping owner is
:mod:`src.infrastructure.search.music_index_template`.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Iterable

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.persistence.models import MusicSchoolDocumentModel
from src.infrastructure.search.music_index_template import ALIAS

log = logging.getLogger("search.music_indexer")


def _iso(value) -> str | None:
    """Render dates/datetimes for ES; pass other types through unchanged."""
    if value is None:
        return None
    return value.isoformat()


def _build_es_doc(model: MusicSchoolDocumentModel) -> dict[str, Any]:
    """Project a ``MusicSchoolDocumentModel`` into the ES shape."""
    return {
        "id": str(model.id),
        "student_full_name": model.student_full_name,
        "music_school_id": str(model.music_school_id),
        "music_school_name": model.music_school.name if model.music_school else None,
        "specialty_id": str(model.specialty_id),
        "specialty": model.specialty.name if model.specialty else None,
        "graduation_year": model.graduation_year,
        "diploma_serial": model.diploma_serial,
        "diploma_number": model.diploma_number,
        "given_date": _iso(model.given_date),
        "description": model.description,
        "file_path": model.file_path,
        "passport_series": model.passport_series,
        "passport_number": model.passport_number,
        "pinfl": model.pinfl,
        "extracted_text": model.extracted_text,
        "ocr_status": model.ocr_status,
        "created_by": str(model.created_by) if model.created_by else None,
        "created_at": _iso(model.created_at),
        "updated_at": _iso(model.updated_at),
    }


def _select_with_joins():
    """Eager-load the music school and specialty relationships."""
    return (
        select(MusicSchoolDocumentModel)
        .options(
            selectinload(MusicSchoolDocumentModel.music_school),
            selectinload(MusicSchoolDocumentModel.specialty),
        )
    )


async def index_document(
    es: AsyncElasticsearch,
    session: AsyncSession,
    doc_id: uuid.UUID,
) -> None:
    """Upsert one music school document into ``music_documents`` alias."""
    stmt = _select_with_joins().where(MusicSchoolDocumentModel.id == doc_id)
    result = await session.execute(stmt)
    model = result.scalar_one_or_none()
    if model is None:
        log.info("index_document(%s): row missing in PG → deleting from ES", doc_id)
        await delete_document(es, doc_id)
        return
    body = _build_es_doc(model)
    await es.index(index=ALIAS, id=str(doc_id), body=body)
    log.debug("index_document(%s): indexed", doc_id)


async def delete_document(es: AsyncElasticsearch, doc_id: uuid.UUID) -> None:
    """Delete by id. A missing document is a no-op."""
    try:
        await es.delete(index=ALIAS, id=str(doc_id))
        log.debug("delete_document(%s): deleted from ES", doc_id)
    except NotFoundError:
        log.debug("delete_document(%s): not in ES (no-op)", doc_id)


async def index_bulk(
    es: AsyncElasticsearch,
    session: AsyncSession,
    doc_ids: Iterable[uuid.UUID],
) -> int:
    """Bulk-index a list of music school documents in one round-trip."""
    ids = list(doc_ids)
    if not ids:
        return 0
    stmt = _select_with_joins().where(MusicSchoolDocumentModel.id.in_(ids))
    result = await session.execute(stmt)
    models = result.scalars().unique().all()

    actions = [
        {
            "_op_type": "index",
            "_index": ALIAS,
            "_id": str(m.id),
            "_source": _build_es_doc(m),
        }
        for m in models
    ]
    if not actions:
        return 0

    success, failures = await async_bulk(es, actions, raise_on_error=False)
    if failures:
        log.warning("index_bulk: %d failures (showing first): %s", len(failures), failures[:1])
    return success

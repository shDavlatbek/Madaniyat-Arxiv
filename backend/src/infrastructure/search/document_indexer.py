"""Indexer service: Postgres ``documents`` row → Elasticsearch ``documents`` alias.

Reads one document at a time with its denormalized refs (year, category,
person + active tenure, archive folder, document type, field values,
attachments) and writes a single ES document. The mapping owner is
:mod:`src.infrastructure.search.index_template`.

Phase 5 wires this behind the on-save outbox (Task 5.3) and the reindex CLI
(Task 5.5). Phase 6 will populate the OCR text fields that this mapper
already passes through.
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

from src.infrastructure.persistence.models import (
    DocumentFieldValueModel,
    DocumentModel,
    PersonModel,
)
from src.infrastructure.search.index_template import ALIAS

log = logging.getLogger("search.indexer")


def _iso(value) -> str | None:
    """Render dates/datetimes for ES; pass other types through unchanged."""
    if value is None:
        return None
    return value.isoformat()


def _build_es_doc(model: DocumentModel) -> dict[str, Any]:
    """Project a ``DocumentModel`` (with relationships loaded) into the ES shape.

    Missing FKs (deleted category/person/etc.) collapse to ``None`` rather than
    raising — search must still surface the document.
    """
    return {
        "id": str(model.id),
        # ─── denormalized refs (None when FK target is missing) ──────────
        "year_id": model.year_id,
        "year_value": model.year.value if model.year else None,
        "category_id": str(model.category_id) if model.category_id else None,
        "category_name": model.category.name if model.category else None,
        "person_id": str(model.person_id) if model.person_id else None,
        "person_name": model.person.full_name if model.person else None,
        # Person position is denormalized from the active tenure on the doc
        # date — the existing repo doesn't pre-compute this, so we fall back
        # to the most recent tenure's position rather than running another
        # query path here.
        "person_position": (
            model.person.tenures[0].position
            if model.person and model.person.tenures
            else None
        ),
        "archive_folder_id": str(model.archive_folder_id) if model.archive_folder_id else None,
        "archive_folder_index_code": model.archive_folder.index_code if model.archive_folder else None,
        "archive_folder_title": model.archive_folder.title if model.archive_folder else None,
        "document_type_id": str(model.document_type_id) if model.document_type_id else None,
        "document_type_name": model.document_type.name if model.document_type else None,
        # ─── core document fields ────────────────────────────────────────
        "title": model.title,
        "document_number": model.document_number,
        "short_desc": model.short_desc,
        "signer": model.signer,
        "signed_by": model.signed_by,
        "archive_number": model.archive_number,
        "document_view": model.document_view,
        "document_form": model.document_form,
        "sender": model.sender,
        "language": model.language,
        "related_document_number": model.related_document_number,
        "related_document_date": _iso(model.related_document_date),
        "received_date": _iso(model.received_date),
        "origin_organization": model.origin_organization,
        "sent_date": _iso(model.sent_date),
        "recipient_organization": model.recipient_organization,
        "applicant_full_name": model.applicant_full_name,
        "applicant_phone": model.applicant_phone,
        "person_type": model.person_type,
        "outgoing_number": model.outgoing_number,
        "outgoing_date": _iso(model.outgoing_date),
        "note": model.note,
        "pages": model.pages,
        "date": _iso(model.date),
        "created_at": _iso(model.created_at),
        "updated_at": _iso(model.updated_at),
        # ─── OCR text (filled by the Phase 6 worker; null until then) ───
        "extracted_text": model.extracted_text,
        "ocr_status": model.ocr_status,
        # ─── nested children ─────────────────────────────────────────────
        "attachments": [
            {
                "id": str(a.id),
                "original_filename": a.original_filename,
                "extracted_text": a.extracted_text,
                "ocr_status": a.ocr_status,
            }
            for a in (model.attachments or [])
        ],
        "field_values": [
            {
                "name": fv.category_field.name if fv.category_field else None,
                "label": fv.category_field.label if fv.category_field else None,
                "value": fv.value,
            }
            for fv in (model.field_values or [])
        ],
    }


def _select_with_joins():
    """Eager-load every relationship the ES doc denormalizes."""
    return (
        select(DocumentModel)
        .options(
            selectinload(DocumentModel.year),
            selectinload(DocumentModel.category),
            selectinload(DocumentModel.person).selectinload(PersonModel.tenures),
            selectinload(DocumentModel.archive_folder),
            selectinload(DocumentModel.document_type),
            selectinload(DocumentModel.attachments),
            selectinload(DocumentModel.field_values).selectinload(DocumentFieldValueModel.category_field),
        )
    )


async def index_document(
    es: AsyncElasticsearch,
    session: AsyncSession,
    doc_id: uuid.UUID,
) -> None:
    """Upsert one document into ``documents`` alias. No-op (delete) if the
    Postgres row is gone."""
    stmt = _select_with_joins().where(DocumentModel.id == doc_id)
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
        log.debug("delete_document(%s): deleted", doc_id)
    except NotFoundError:
        log.debug("delete_document(%s): not in ES (no-op)", doc_id)


async def index_bulk(
    es: AsyncElasticsearch,
    session: AsyncSession,
    doc_ids: Iterable[uuid.UUID],
) -> int:
    """Bulk-index a list of documents in one round-trip. Returns the count
    written."""
    ids = list(doc_ids)
    if not ids:
        return 0
    stmt = _select_with_joins().where(DocumentModel.id.in_(ids))
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

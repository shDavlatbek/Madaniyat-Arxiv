"""arq worker bootstrap.

Hosts the background-task runtime that supports:

* Phase 5.4 — :func:`drain_search_outbox`: every 2 s, drain
  ``search_index_jobs`` and apply each pending change to Elasticsearch.
* Phase 6 — OCR pipeline (lands later).

Run with::

    uv run arq src.infrastructure.jobs.worker.WorkerSettings

or via ``make worker``.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from arq import cron
from arq.connections import RedisSettings
from sqlalchemy import select

from src.infrastructure.config import settings
from src.infrastructure.ocr.ocr_service import extract_text
from src.infrastructure.persistence.database import async_session
from src.infrastructure.persistence.models import (
    DocumentAttachmentModel,
    DocumentModel,
    MusicSchoolDocumentModel,
    SearchIndexJobModel,
)
from src.infrastructure.search.document_indexer import (
    delete_document as delete_general_document,
    index_document as index_general_document,
)
from src.infrastructure.search.music_document_indexer import (
    delete_document as delete_music_document,
    index_document as index_music_document,
)
from src.infrastructure.search.es_client import close_es, get_es
from src.infrastructure.search.index_template import ensure_index as ensure_general_index
from src.infrastructure.search.music_index_template import ensure_index as ensure_music_index

log = logging.getLogger("worker")

# How many outbox rows to drain per tick. Sized so one drain doesn't hold the
# session locked for more than ~a second on a sane corpus.
DRAIN_BATCH_SIZE = 100


def _redis_settings_from_url(url: str) -> RedisSettings:
    """Parse a ``redis://host:port/db`` URL into ``RedisSettings``."""
    parsed = urlparse(url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or "0"),
        password=parsed.password,
    )


async def health_check(ctx: dict) -> str:
    """Placeholder job — enqueue this to prove the worker is alive."""
    log.info("health_check: ok (job_id=%s)", ctx.get("job_id"))
    return "ok"


async def ocr_extract(
    ctx: dict,
    document_id: str,
    attachment_id: str | None = None,
) -> str:
    """Extract OCR text from a document's main file or one of its attachments.

    Flow per row:
      pending → processing  (flushed before the CPU work so the UI sees it)
      processing → done    (success: text + completed_at written)
      processing → failed  (any exception: status flipped, request not blocked)
      processing → skipped (no file_path attached — nothing to OCR)

    On success an outbox row is appended so the search drain reindexes the
    document with the new text.

    ``extract_text`` is CPU-bound; we hand it to a thread executor so the
    arq event loop stays responsive to other jobs.
    """
    doc_uuid = uuid.UUID(document_id)
    att_uuid = uuid.UUID(attachment_id) if attachment_id else None
    log.info("ocr_extract: doc=%s attachment=%s", doc_uuid, att_uuid)

    async with async_session() as s:
        entity_type = "general"
        if att_uuid is None:
            target = await s.get(DocumentModel, doc_uuid)
            if target is None:
                target = await s.get(MusicSchoolDocumentModel, doc_uuid)
                entity_type = "music_school"
            label = f"{entity_type} doc {doc_uuid}"
        else:
            target = await s.get(DocumentAttachmentModel, att_uuid)
            label = f"attachment {att_uuid}"

        if target is None:
            log.warning("ocr_extract: %s vanished before processing — skipped", label)
            return "missing"

        if not target.file_path:
            target.ocr_status = "skipped"
            target.ocr_completed_at = datetime.utcnow()
            await s.commit()
            return "skipped"

        file_path = Path(target.file_path)
        if not file_path.exists():
            log.error("ocr_extract: %s — file not found at %s", label, file_path)
            target.ocr_status = "failed"
            target.ocr_completed_at = datetime.utcnow()
            await s.commit()
            return "failed"

        target.ocr_status = "processing"
        await s.commit()

        loop = asyncio.get_running_loop()
        try:
            text = await loop.run_in_executor(None, extract_text, file_path)
        except Exception:  # noqa: BLE001
            log.exception("ocr_extract: %s failed", label)
            target.ocr_status = "failed"
            target.ocr_completed_at = datetime.utcnow()
            await s.commit()
            return "failed"

        target.extracted_text = text or None
        target.ocr_status = "done"
        target.ocr_completed_at = datetime.utcnow()
        # Re-index so ES picks up the new extracted_text.
        s.add(SearchIndexJobModel(document_id=doc_uuid, op="index", entity_type=entity_type))
        await s.commit()
        log.info("ocr_extract: %s done (%d chars)", label, len(text or ""))
        return "done"
async def drain_search_outbox(ctx: dict) -> int:
    """Drain up to ``DRAIN_BATCH_SIZE`` rows from ``search_index_jobs``."""
    es = get_es()
    processed = 0
    async with async_session() as s:
        stmt = (
            select(SearchIndexJobModel)
            .order_by(SearchIndexJobModel.created_at)
            .limit(DRAIN_BATCH_SIZE)
        )
        rows = (await s.execute(stmt)).scalars().all()
        if not rows:
            return 0

        for row in rows:
            try:
                is_music = row.entity_type == "music_school"
                if row.op == "index":
                    if is_music:
                        await index_music_document(es, s, row.document_id)
                    else:
                        await index_general_document(es, s, row.document_id)
                elif row.op == "delete":
                    if is_music:
                        await delete_music_document(es, row.document_id)
                    else:
                        await delete_general_document(es, row.document_id)
                else:
                    log.warning("drain: unknown op %r on row %s — dropping", row.op, row.id)
                await s.delete(row)
                await s.flush()
                processed += 1
            except Exception:  # noqa: BLE001
                log.exception("drain: failed for outbox row %s op=%s", row.id, row.op)
                break

        await s.commit()

    if processed:
        log.info("drain: %d outbox row(s) applied", processed)
    return processed


async def startup(ctx: dict) -> None:
    log.info("worker startup: redis=%s, elasticsearch=%s", settings.redis_url, settings.elasticsearch_url)
    try:
        await ensure_general_index(get_es())
    except Exception as exc:  # noqa: BLE001
        log.warning("ensure_general_index failed at worker startup: %s", exc)
    try:
        await ensure_music_index(get_es())
    except Exception as exc:  # noqa: BLE001
        log.warning("ensure_music_index failed at worker startup: %s", exc)


async def shutdown(ctx: dict) -> None:
    log.info("worker shutdown")
    await close_es()


class WorkerSettings:
    """arq picks this up by reference; see https://arq-docs.helpmanual.io/."""

    functions = [health_check, drain_search_outbox, ocr_extract]
    # Every even second — close enough to "every 2 s" for a single-worker setup.
    cron_jobs = [
        cron(drain_search_outbox, second=set(range(0, 60, 2)), run_at_startup=True),
    ]
    redis_settings = _redis_settings_from_url(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown

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

import logging
from urllib.parse import urlparse

from arq import cron
from arq.connections import RedisSettings
from sqlalchemy import select

from src.infrastructure.config import settings
from src.infrastructure.persistence.database import async_session
from src.infrastructure.persistence.models import SearchIndexJobModel
from src.infrastructure.search.document_indexer import delete_document, index_document
from src.infrastructure.search.es_client import close_es, get_es
from src.infrastructure.search.index_template import ensure_index

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


async def drain_search_outbox(ctx: dict) -> int:
    """Drain up to ``DRAIN_BATCH_SIZE`` rows from ``search_index_jobs``.

    Each row is processed independently: on success the outbox row is deleted
    in the same transaction; on Elasticsearch failure the row stays so the
    next tick retries. A row whose ``document_id`` no longer exists in
    Postgres collapses to a delete via :func:`index_document`'s internal
    handling — it's idempotent.

    Returns the number of rows processed (useful in tests).
    """
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
                if row.op == "index":
                    await index_document(es, s, row.document_id)
                elif row.op == "delete":
                    await delete_document(es, row.document_id)
                else:
                    log.warning("drain: unknown op %r on row %s — dropping", row.op, row.id)
                await s.delete(row)
                await s.flush()
                processed += 1
            except Exception:  # noqa: BLE001
                # Bail without committing the row delete; it retries next tick.
                # The earlier rows in this batch are already flushed and will
                # be committed below — that's intentional: partial progress is
                # safer than rolling back successful work for one failure.
                log.exception("drain: failed for outbox row %s op=%s", row.id, row.op)
                break

        await s.commit()

    if processed:
        log.info("drain: %d outbox row(s) applied", processed)
    return processed


async def startup(ctx: dict) -> None:
    log.info("worker startup: redis=%s, elasticsearch=%s", settings.redis_url, settings.elasticsearch_url)
    try:
        await ensure_index(get_es())
    except Exception as exc:  # noqa: BLE001
        log.warning("ensure_index failed at worker startup: %s", exc)


async def shutdown(ctx: dict) -> None:
    log.info("worker shutdown")
    await close_es()


class WorkerSettings:
    """arq picks this up by reference; see https://arq-docs.helpmanual.io/."""

    functions = [health_check, drain_search_outbox]
    # Every even second — close enough to "every 2 s" for a single-worker setup.
    cron_jobs = [
        cron(drain_search_outbox, second=set(range(0, 60, 2)), run_at_startup=True),
    ]
    redis_settings = _redis_settings_from_url(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown

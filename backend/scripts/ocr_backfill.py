"""Backfill OCR for every document + attachment that hasn't been processed.

Walks ``documents`` and ``document_attachments`` for rows with
``ocr_status`` in the configured set, enqueues an ``ocr_extract`` job per
row through arq, and waits for each result. A semaphore caps in-flight
work at ``--concurrency`` (default 4) so we don't slam Tesseract — the
worker itself can run more, but the CLI is the one paying for failures
to land in the DB before exiting.

Usage::

    cd backend
    uv run python -m scripts.ocr_backfill              # only ocr_status='pending'
    uv run python -m scripts.ocr_backfill --retry-failed
    uv run python -m scripts.ocr_backfill --concurrency 8

Resume-safe: a row whose ``ocr_status`` is already ``done`` is skipped, so
re-running the CLI after partial progress only picks up the remainder.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import uuid

from arq import create_pool
from sqlalchemy import select

from src.infrastructure.jobs.worker import WorkerSettings
from src.infrastructure.persistence.database import async_session
from src.infrastructure.persistence.models import DocumentAttachmentModel, DocumentModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ocr_backfill")

# Per-job arq result timeout. Generous because scanned PDFs with many pages
# can sit in Tesseract for ~30 s each.
JOB_TIMEOUT = 600


async def _list_candidates(statuses: list[str]) -> tuple[list[uuid.UUID], list[tuple[uuid.UUID, uuid.UUID]]]:
    async with async_session() as s:
        doc_rows = (await s.execute(
            select(DocumentModel.id)
            .where(DocumentModel.ocr_status.in_(statuses))
            .where(DocumentModel.file_path.is_not(None))
        )).scalars().all()
        att_rows = (await s.execute(
            select(DocumentAttachmentModel.document_id, DocumentAttachmentModel.id)
            .where(DocumentAttachmentModel.ocr_status.in_(statuses))
        )).all()
    return list(doc_rows), [(row[0], row[1]) for row in att_rows]


async def run(concurrency: int, retry_failed: bool) -> int:
    statuses = ["pending"]
    if retry_failed:
        statuses.append("failed")

    docs, atts = await _list_candidates(statuses)
    total = len(docs) + len(atts)
    log.info("OCR backfill: %d documents + %d attachments (statuses=%s, concurrency=%d)",
             len(docs), len(atts), statuses, concurrency)
    if total == 0:
        return 0

    pool = await create_pool(WorkerSettings.redis_settings)
    sem = asyncio.Semaphore(concurrency)

    async def one(doc_id: uuid.UUID, att_id: uuid.UUID | None) -> str:
        async with sem:
            args = (str(doc_id),) if att_id is None else (str(doc_id), str(att_id))
            job = await pool.enqueue_job("ocr_extract", *args)
            try:
                return await job.result(timeout=JOB_TIMEOUT)
            except Exception:  # noqa: BLE001
                log.exception("backfill: job for doc=%s att=%s timed out", doc_id, att_id)
                return "timeout"

    tasks = [one(d, None) for d in docs] + [one(d, a) for d, a in atts]

    done = 0
    summary: dict[str, int] = {}
    for coro in asyncio.as_completed(tasks):
        result = await coro
        summary[result] = summary.get(result, 0) + 1
        done += 1
        if done % 10 == 0 or done == total:
            log.info("  progress: %d / %d (%s)", done, total, summary)

    await pool.aclose()
    log.info("OCR backfill complete: %s", summary)
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--retry-failed", action="store_true",
                        help="Also re-enqueue rows whose ocr_status is 'failed' (default skips them).")
    args = parser.parse_args()
    asyncio.run(run(concurrency=args.concurrency, retry_failed=args.retry_failed))
    return 0


if __name__ == "__main__":
    sys.exit(main())

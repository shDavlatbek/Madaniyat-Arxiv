"""Full-corpus reindex by appending outbox rows.

Walks every document matching the given filters and inserts one
``search_index_jobs`` row per document. The running ``arq`` worker drains
those rows the same way it handles live writes — so this script never talks
to Elasticsearch directly. That keeps reindex semantics identical to normal
indexing and lets reindex happen in the background while the app serves
traffic.

Usage::

    cd backend
    uv run python -m scripts.reindex                  # everything
    uv run python -m scripts.reindex --year 2024
    uv run python -m scripts.reindex --since 2024-01-01
    uv run python -m scripts.reindex --dry-run        # report-only

Run after schema changes that affect denormalized fields, mapping updates,
or alias swaps (``documents-v2`` → ``documents-v1``).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.infrastructure.persistence.database import async_session
from src.infrastructure.persistence.models import DocumentModel, SearchIndexJobModel, YearModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("reindex")

BATCH_SIZE = 500


async def run(year: int | None, since: date | None, dry_run: bool) -> int:
    async with async_session() as s:
        stmt = select(DocumentModel.id)
        if year is not None:
            stmt = stmt.join(YearModel, YearModel.id == DocumentModel.year_id).where(YearModel.value == year)
        if since is not None:
            stmt = stmt.where(DocumentModel.updated_at >= since)

        ids = (await s.execute(stmt)).scalars().all()
        log.info("Reindex candidates: %d (year=%s, since=%s, dry_run=%s)", len(ids), year, since, dry_run)

        if dry_run or not ids:
            return len(ids)

        # Append outbox rows in batches.
        for offset in range(0, len(ids), BATCH_SIZE):
            batch = ids[offset:offset + BATCH_SIZE]
            for doc_id in batch:
                s.add(SearchIndexJobModel(document_id=doc_id, op="index"))
            await s.flush()
            log.info("  enqueued %d/%d", min(offset + BATCH_SIZE, len(ids)), len(ids))
        await s.commit()
        log.info("Done — %d outbox rows enqueued. The worker will drain them.", len(ids))
    return len(ids)


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, help="Filter by year value (e.g. 2024)")
    parser.add_argument("--since", type=_parse_date, help="Only docs with updated_at >= ISO date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Report counts without writing")
    args = parser.parse_args()

    asyncio.run(run(year=args.year, since=args.since, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    sys.exit(main())

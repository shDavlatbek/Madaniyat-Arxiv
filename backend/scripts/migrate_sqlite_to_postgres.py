"""One-shot data migration: SQLite → PostgreSQL.

Reads every table from the source SQLite database in FK dependency order and
inserts the rows into a target PostgreSQL database. Type adaptation (str→UUID,
str→date, str→datetime, str→dict for JSON) is driven by the SQLAlchemy
metadata declared in :mod:`src.infrastructure.persistence.models`.

Usage:
    uv run python -m scripts.migrate_sqlite_to_postgres \\
        --source-url sqlite+aiosqlite:///./arxiv_db.db \\
        --target-url postgresql+asyncpg://postgres:pw@localhost:5432/arxiv_db \\
        --yes-i-mean-it

Both URLs default to the ``SOURCE_DATABASE_URL`` / ``TARGET_DATABASE_URL`` env
vars when omitted.

Idempotency: the script refuses to run against a non-empty target unless
``--yes-i-mean-it`` is passed, in which case every target table is truncated
in reverse FK order before inserts begin.

Dry-run mode (``--dry-run``) reads from the source and validates counts but
performs no writes.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import MetaData, Table, text
from sqlalchemy.ext.asyncio import create_async_engine

from src.infrastructure.persistence.models import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("migrate_sqlite_to_postgres")


# Parents before children — order matters for FK satisfiability during INSERT.
TABLE_ORDER: list[str] = [
    "years",
    "departments",
    "categories",
    "category_fields",
    "default_fields",
    "document_types",
    "regions",
    "reception_places",
    "appeal_types",
    "retention_periods",
    "persons",
    "person_tenures",
    "archive_folders",
    "users",
    "documents",
    "document_field_values",
    "document_attachments",
]


def _adapt_value(value: Any, col_type_name: str) -> Any:
    """Coerce a SQLite TEXT/INT value to the Python type the PG column expects."""
    if value is None:
        return None
    if col_type_name == "GUID":
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
    if col_type_name == "JSONType":
        if isinstance(value, (dict, list)):
            return value
        return json.loads(value)
    if col_type_name == "Date":
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        return date.fromisoformat(str(value))
    if col_type_name == "DateTime":
        if isinstance(value, datetime):
            return value
        # SQLite emits like "2024-01-15 10:30:45.123456" — fromisoformat handles this in 3.11+.
        return datetime.fromisoformat(str(value).replace(" ", "T"))
    if col_type_name == "Boolean":
        # SQLite stores booleans as 0/1.
        return bool(value)
    return value


_PATH_COLUMNS = {"file_path"}


def _adapt_row(row: dict, table: Table) -> dict:
    out: dict = {}
    for col_name, col in table.columns.items():
        if col_name not in row:
            continue
        type_name = type(col.type).__name__
        value = _adapt_value(row[col_name], type_name)
        # Normalize Windows backslashes in stored file paths so a Linux
        # OCR worker can resolve a path written by a Windows backend.
        if col_name in _PATH_COLUMNS and isinstance(value, str):
            value = value.replace("\\", "/")
        out[col_name] = value
    return out


async def _row_count(conn, table_name: str) -> int:
    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
    return result.scalar_one()


async def _truncate_target(conn, metadata: MetaData) -> None:
    log.warning("Truncating target tables (reverse FK order)…")
    for table_name in reversed(TABLE_ORDER):
        await conn.execute(text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE'))
    log.info("Target truncated.")


async def _migrate_table(source_conn, target_conn, table: Table) -> tuple[int, int]:
    """Returns (source_count, inserted_count)."""
    source_rows = (await source_conn.execute(text(f'SELECT * FROM "{table.name}"'))).mappings().all()
    source_count = len(source_rows)
    if source_count == 0:
        return 0, 0

    adapted = [_adapt_row(dict(row), table) for row in source_rows]
    await target_conn.execute(table.insert(), adapted)
    return source_count, len(adapted)


async def _resync_sequences(target_conn) -> None:
    """Postgres autoincrement sequences need bumping past the max id after bulk insert."""
    # Only ``years.id`` uses a Postgres SERIAL — everything else is a UUID.
    await target_conn.execute(
        text("SELECT setval(pg_get_serial_sequence('years', 'id'), COALESCE((SELECT MAX(id) FROM years), 1))")
    )


async def run(
    source_url: str,
    target_url: str,
    *,
    confirm: bool,
    dry_run: bool,
) -> int:
    log.info("Source: %s", source_url)
    log.info("Target: %s", target_url)
    log.info("Dry-run: %s", dry_run)

    metadata: MetaData = Base.metadata

    source_engine = create_async_engine(source_url)
    target_engine = create_async_engine(target_url)

    total_source = 0
    total_inserted = 0
    mismatches: list[tuple[str, int, int]] = []

    try:
        async with source_engine.connect() as src, target_engine.connect() as tgt:
            # Check target is empty unless --yes-i-mean-it.
            if not dry_run:
                non_empty = []
                for t in TABLE_ORDER:
                    if await _row_count(tgt, t) > 0:
                        non_empty.append(t)
                if non_empty and not confirm:
                    log.error("Target has data in: %s. Re-run with --yes-i-mean-it to truncate.", non_empty)
                    return 2
                if non_empty:
                    await _truncate_target(tgt, metadata)

            # Copy each table.
            for table_name in TABLE_ORDER:
                table = metadata.tables[table_name]
                if dry_run:
                    src_count = await _row_count(src, table_name)
                    log.info("  [%s] %s rows in source (dry-run, no write)", table_name, src_count)
                    total_source += src_count
                    continue

                src_count, inserted = await _migrate_table(src, tgt, table)
                await tgt.commit()
                total_source += src_count
                total_inserted += inserted

                # Re-read target row count to confirm.
                tgt_count = await _row_count(tgt, table_name)
                marker = "✓" if tgt_count == src_count else "✗"
                log.info("  %s [%s] source=%d inserted=%d target=%d", marker, table_name, src_count, inserted, tgt_count)
                if tgt_count != src_count:
                    mismatches.append((table_name, src_count, tgt_count))

            # Re-sync PG sequences for autoincrement columns.
            if not dry_run:
                await _resync_sequences(tgt)
                await tgt.commit()
    finally:
        await source_engine.dispose()
        await target_engine.dispose()

    log.info("Total: source=%d inserted=%d", total_source, total_inserted)
    if mismatches:
        log.error("Row count mismatches: %s", mismatches)
        return 1
    log.info("OK — migration complete.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=os.environ.get("SOURCE_DATABASE_URL"))
    parser.add_argument("--target-url", default=os.environ.get("TARGET_DATABASE_URL"))
    parser.add_argument("--yes-i-mean-it", dest="confirm", action="store_true",
                        help="Truncate non-empty target tables before inserts.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report counts without writing.")
    args = parser.parse_args()

    if not args.source_url:
        parser.error("--source-url (or SOURCE_DATABASE_URL env var) required")
    if not args.target_url:
        parser.error("--target-url (or TARGET_DATABASE_URL env var) required")

    return asyncio.run(run(
        source_url=args.source_url,
        target_url=args.target_url,
        confirm=args.confirm,
        dry_run=args.dry_run,
    ))


if __name__ == "__main__":
    sys.exit(main())

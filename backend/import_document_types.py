"""
Import document types (Hujjat turi) from a JSON file into the database.

The JSON file is a list of objects with `id` (UUID string) and `name`. Existing
explicit UUIDs are preserved. The script is idempotent — run it as many times as
you like:
  - a row whose `id` is already present has its `name` refreshed;
  - a new `id` is inserted;
  - a `name` already taken by a different `id` is skipped (the unique-name
    constraint would otherwise reject it).

The `d8f3a2c1e9b4` migration performs the same seed on a fresh DB; this script
is for re-syncing an existing DB after `types.json` changes.

Usage:
  python import_document_types.py
  python import_document_types.py --file types.json

Inside Docker:
  docker compose exec backend uv run python import_document_types.py
"""

import argparse
import asyncio
import json
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.config import settings
from src.infrastructure.persistence.models import DocumentTypeModel


async def import_document_types(file_path: Path) -> None:
    if not file_path.exists():
        print(f"Fayl topilmadi: {file_path}")
        return

    entries = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        print("JSON fayl ro'yxat (list) bo'lishi kerak.")
        return

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    created = 0
    updated = 0
    skipped = 0

    async with session_factory() as session:
        for entry in entries:
            raw_id = (entry or {}).get("id")
            name = ((entry or {}).get("name") or "").strip()
            if not raw_id or not name:
                skipped += 1
                continue
            try:
                type_id = uuid.UUID(str(raw_id))
            except (ValueError, TypeError):
                print(f"  - Yaroqsiz UUID, o'tkazib yuborildi: {raw_id!r}")
                skipped += 1
                continue

            existing = await session.get(DocumentTypeModel, type_id)
            if existing:
                if existing.name != name:
                    clash = await session.execute(
                        select(DocumentTypeModel).where(DocumentTypeModel.name == name)
                    )
                    clash = clash.scalar_one_or_none()
                    if clash and clash.id != type_id:
                        print(f"  - Nom band, o'tkazib yuborildi: {name!r}")
                        skipped += 1
                        continue
                    existing.name = name
                    updated += 1
                continue

            clash = await session.execute(
                select(DocumentTypeModel).where(DocumentTypeModel.name == name)
            )
            if clash.scalar_one_or_none():
                print(f"  - Nom band (boshqa id), o'tkazib yuborildi: {name!r}")
                skipped += 1
                continue

            session.add(DocumentTypeModel(id=type_id, name=name))
            created += 1

        await session.commit()

    await engine.dispose()
    print(f"Tayyor. Qo'shildi: {created}, yangilandi: {updated}, o'tkazib yuborildi: {skipped}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="types.json dan hujjat turlarini bazaga import qilish"
    )
    parser.add_argument(
        "--file",
        default=str(Path(__file__).resolve().parent / "data/types.json"),
        help="JSON fayl yo'li (default: backend/types.json)",
    )
    args = parser.parse_args()
    asyncio.run(import_document_types(Path(args.file)))


if __name__ == "__main__":
    main()

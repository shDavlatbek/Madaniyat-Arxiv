"""
Import Murojaat (appeal) reference data from JSON files into the database.

Covers three tables:
  - regions          <- data/region-local.json + data/region-abroad.json
  - reception_places <- data/Qabul qilingan joy.json
  - appeal_types     <- data/Murojaat turi.json

Each JSON file is a list of objects with `id` (UUID string) and `name`
(region files also carry `type`). Explicit UUIDs are preserved. The script is
idempotent — run it as many times as you like:
  - a row whose `id` is already present has its `name`/`type` refreshed;
  - a new `id` is inserted;
  - an entry missing `id` or `name` is skipped.

The `a3f1c2d4e5b6` migration performs the same seed on a fresh DB; this script
is for re-syncing an existing DB after the JSON files change.

Usage:
  python import_reference_data.py
  python import_reference_data.py --data-dir data

Inside Docker:
  docker compose exec backend uv run python import_reference_data.py
"""

import argparse
import asyncio
import json
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.config import settings
from src.infrastructure.persistence.models import (
    AppealTypeModel,
    ReceptionPlaceModel,
    RegionModel,
)


def _load(path: Path) -> list:
    if not path.exists():
        print(f"  Fayl topilmadi, o'tkazib yuborildi: {path.name}")
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


async def _sync(session: AsyncSession, model, rows: list[dict], fields: tuple[str, ...]) -> tuple[int, int, int]:
    """Upsert `rows` into `model` by primary-key id. Returns (created, updated, skipped)."""
    created = updated = skipped = 0
    for row in rows:
        raw_id = row.get("id")
        name = (row.get("name") or "").strip()
        if not raw_id or not name:
            skipped += 1
            continue
        try:
            pk = uuid.UUID(str(raw_id))
        except (ValueError, TypeError):
            print(f"  - Yaroqsiz UUID, o'tkazib yuborildi: {raw_id!r}")
            skipped += 1
            continue

        values = {"name": name}
        if "type" in fields:
            values["type"] = (row.get("type") or "").strip().upper()

        existing = await session.get(model, pk)
        if existing:
            if any(getattr(existing, k) != v for k, v in values.items()):
                for k, v in values.items():
                    setattr(existing, k, v)
                updated += 1
        else:
            session.add(model(id=pk, **values))
            created += 1
    return created, updated, skipped


async def import_reference_data(data_dir: Path) -> None:
    region_rows: list[dict] = []
    for filename in ("region-local.json", "region-abroad.json"):
        region_rows.extend(_load(data_dir / filename))
    reception_rows = _load(data_dir / "Qabul qilingan joy.json")
    appeal_rows = _load(data_dir / "Murojaat turi.json")

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        for label, model, rows, fields in (
            ("Hududlar", RegionModel, region_rows, ("name", "type")),
            ("Qabul qilingan joylar", ReceptionPlaceModel, reception_rows, ("name",)),
            ("Murojaat turlari", AppealTypeModel, appeal_rows, ("name",)),
        ):
            created, updated, skipped = await _sync(session, model, rows, fields)
            print(f"{label}: qo'shildi {created}, yangilandi {updated}, o'tkazib yuborildi {skipped}.")
        await session.commit()

    await engine.dispose()
    print("Tayyor.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="JSON fayllardan murojaat ma'lumotnomalarini bazaga import qilish"
    )
    parser.add_argument(
        "--data-dir",
        default=str(Path(__file__).resolve().parent / "data"),
        help="JSON fayllar joylashgan papka (default: backend/data)",
    )
    args = parser.parse_args()
    asyncio.run(import_reference_data(Path(args.data_dir)))


if __name__ == "__main__":
    main()

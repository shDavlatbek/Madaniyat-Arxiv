"""
Database seed script for Music Schools, Music School Users, and Documents.

Usage:
  uv run python seed_music_schools.py
"""

import asyncio
import uuid
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.auth.password_service import hash_password
from src.infrastructure.config import settings
from src.infrastructure.persistence.models import MusicSchoolModel, UserModel, MusicSchoolDocumentModel


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        print("Music School seeding started...")

        # 1. Create Music Schools
        schools_to_create = [
            {"id": uuid.UUID("11111111-1111-1111-1111-111111111111"), "name": "Toshkent shahar 1-sonli bolalar musiqa va san'at maktabi", "code": "TSMS01"},
            {"id": uuid.UUID("22222222-2222-2222-2222-222222222222"), "name": "Samarqand shahar 2-sonli bolalar musiqa va san'at maktabi", "code": "SAMMS02"}
        ]

        school_ids = {}
        for s in schools_to_create:
            res = await session.execute(select(MusicSchoolModel).where(MusicSchoolModel.name == s["name"]))
            existing = res.scalar_one_or_none()
            if not existing:
                school = MusicSchoolModel(id=s["id"], name=s["name"], code=s["code"])
                session.add(school)
                school_ids[s["code"]] = s["id"]
                print(f"Created Music School: {s['name']}")
            else:
                school_ids[s["code"]] = existing.id
                print(f"Music School already exists: {s['name']}")

        await session.flush()

        # 2. Create Users
        users_to_create = [
            {
                "username": "music1",
                "name": "Toshkent Maktab Operator",
                "password": "password",
                "role": "music_school",
                "music_school_id": school_ids["TSMS01"]
            },
            {
                "username": "music2",
                "name": "Samarqand Maktab Operator",
                "password": "password",
                "role": "music_school",
                "music_school_id": school_ids["SAMMS02"]
            },
            {
                "username": "admin",
                "name": "Bosh Administrator",
                "password": "admin",
                "role": "admin",
                "music_school_id": None
            }
        ]

        for u in users_to_create:
            res = await session.execute(select(UserModel).where(UserModel.username == u["username"]))
            existing = res.scalar_one_or_none()
            if not existing:
                user = UserModel(
                    id=uuid.uuid4(),
                    username=u["username"],
                    name=u["name"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                    music_school_id=u["music_school_id"],
                    is_active=True
                )
                session.add(user)
                print(f"Created User: {u['username']} ({u['role']})")
            else:
                existing.music_school_id = u["music_school_id"]
                existing.role = u["role"]
                print(f"Updated User role/school: {u['username']}")

        await session.flush()

        # 3. Create Documents
        docs_to_create = [
            {
                "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
                "student_full_name": "Alisher Nabiyev",
                "music_school_id": school_ids["TSMS01"],
                "specialty": "Forte-piano (Fortepiano)",
                "graduation_year": 2024,
                "diploma_serial": "BMS",
                "diploma_number": "123456",
                "given_date": datetime.date(2024, 5, 20),
                "description": "Forte-piano sinfi bo'yicha imtiyozli bitiruv diplom hujjati."
            },
            {
                "id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
                "student_full_name": "Dilnoza Soliyeva",
                "music_school_id": school_ids["SAMMS02"],
                "specialty": "G'ijjak (Gijjak)",
                "graduation_year": 2025,
                "diploma_serial": "BMS",
                "diploma_number": "987654",
                "given_date": datetime.date(2025, 5, 15),
                "description": "G'ijjak sinfi bo'yicha imtiyozli bitiruv diplom hujjati."
            }
        ]

        for d in docs_to_create:
            res = await session.execute(select(MusicSchoolDocumentModel).where(MusicSchoolDocumentModel.id == d["id"]))
            existing = res.scalar_one_or_none()
            if not existing:
                doc = MusicSchoolDocumentModel(
                    id=d["id"],
                    student_full_name=d["student_full_name"],
                    music_school_id=d["music_school_id"],
                    specialty=d["specialty"],
                    graduation_year=d["graduation_year"],
                    diploma_serial=d["diploma_serial"],
                    diploma_number=d["diploma_number"],
                    given_date=d["given_date"],
                    description=d["description"],
                    ocr_status="skipped"
                )
                session.add(doc)
                print(f"Created Document: {d['student_full_name']}")
            else:
                print(f"Document already exists: {d['student_full_name']}")

        await session.commit()
        print("Database seeded successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

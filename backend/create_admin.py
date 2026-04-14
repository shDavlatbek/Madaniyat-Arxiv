"""
Create an admin user for the Arxiv system.

Usage:
  python create_admin.py
  python create_admin.py --username admin --password admin123 --name "Administrator"

Inside Docker:
  docker compose exec backend uv run python create_admin.py
"""

import argparse
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.auth.password_service import hash_password
from src.infrastructure.config import settings
from src.infrastructure.persistence.models import UserModel


async def create_admin(username: str, password: str, name: str, email: str | None = None):
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Check if user already exists
        result = await session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Foydalanuvchi '{username}' allaqachon mavjud.")
            update = input("Parolni yangilamoqchimisiz? (ha/yo'q): ").strip().lower()
            if update in ("ha", "h", "yes", "y"):
                existing.hashed_password = hash_password(password)
                existing.role = "admin"
                existing.is_active = True
                await session.commit()
                print(f"'{username}' paroli yangilandi va admin roli berildi.")
            else:
                print("Bekor qilindi.")
            return

        user = UserModel(
            id=uuid.uuid4(),
            username=username,
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(user)
        await session.commit()
        print(f"Admin foydalanuvchi yaratildi: {username}")

    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Arxiv tizimi uchun admin foydalanuvchi yaratish")
    parser.add_argument("--username", default="admin", help="Foydalanuvchi nomi (default: admin)")
    parser.add_argument("--password", default=None, help="Parol")
    parser.add_argument("--name", default="Administrator", help="To'liq ism (default: Administrator)")
    parser.add_argument("--email", default=None, help="Email (ixtiyoriy)")
    args = parser.parse_args()

    password = args.password
    if not password:
        import getpass
        password = getpass.getpass("Parol kiriting: ")
        if not password:
            print("Parol bo'sh bo'lishi mumkin emas.")
            return

    asyncio.run(create_admin(args.username, password, args.name, args.email))


if __name__ == "__main__":
    main()

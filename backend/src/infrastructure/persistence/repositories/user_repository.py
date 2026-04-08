import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.entity import User
from src.domain.user.repository import UserRepository
from src.infrastructure.persistence.mappers.user_mapper import UserMapper
from src.infrastructure.persistence.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, user_id: uuid.UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return UserMapper.to_domain(model) if model else None

    async def find_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    async def find_all(self, page: int = 1, page_size: int = 20, search: str | None = None) -> tuple[list[User], int]:
        stmt = select(UserModel)
        count_stmt = select(func.count()).select_from(UserModel)

        if search:
            search_filter = or_(
                UserModel.username.ilike(f"%{search}%"),
                UserModel.name.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.order_by(UserModel.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(stmt)
        return [UserMapper.to_domain(m) for m in result.scalars().all()], total

    async def save(self, user: User) -> User:
        existing = await self._session.get(UserModel, user.id)
        if existing:
            UserMapper.update_model(existing, user)
            await self._session.flush()
            return UserMapper.to_domain(existing)
        else:
            model = UserMapper.to_model(user)
            self._session.add(model)
            await self._session.flush()
            return UserMapper.to_domain(model)

    async def delete(self, user_id: uuid.UUID) -> None:
        model = await self._session.get(UserModel, user_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

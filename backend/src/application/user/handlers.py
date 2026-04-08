from __future__ import annotations

from passlib.context import CryptContext

from src.domain.shared.errors import NotFoundError, ValidationError
from src.domain.user.entity import User
from src.domain.user.repository import UserRepository
from src.domain.user.value_objects import UserRole

from .commands import ChangePasswordCommand, CreateUserCommand, DeleteUserCommand, UpdateUserCommand
from .queries import GetUserQuery, ListUsersQuery

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCommandHandler:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def create(self, command: CreateUserCommand) -> User:
        existing = await self._user_repo.find_by_username(command.username)
        if existing:
            raise ValidationError(f"Username '{command.username}' already exists")

        user = User(
            username=command.username,
            name=command.name,
            email=command.email,
            hashed_password=pwd_context.hash(command.password),
            role=UserRole(command.role),
            is_active=command.is_active,
        )
        return await self._user_repo.save(user)

    async def update(self, command: UpdateUserCommand) -> User:
        user = await self._user_repo.find_by_id(command.user_id)
        if not user:
            raise NotFoundError("User", str(command.user_id))

        role = UserRole(command.role) if command.role else None
        user.update(name=command.name, email=command.email, role=role, is_active=command.is_active)
        return await self._user_repo.save(user)

    async def delete(self, command: DeleteUserCommand) -> None:
        await self._user_repo.delete(command.user_id)

    async def change_password(self, command: ChangePasswordCommand) -> User:
        user = await self._user_repo.find_by_id(command.user_id)
        if not user:
            raise NotFoundError("User", str(command.user_id))
        user.change_password(pwd_context.hash(command.new_password))
        return await self._user_repo.save(user)


class UserQueryHandler:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def list_users(self, query: ListUsersQuery) -> tuple[list[User], int]:
        return await self._user_repo.find_all(query.page, query.page_size, query.search)

    async def get_user(self, query: GetUserQuery) -> User:
        user = await self._user_repo.find_by_id(query.user_id)
        if not user:
            raise NotFoundError("User", str(query.user_id))
        return user

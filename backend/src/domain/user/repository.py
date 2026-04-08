from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.user.entity import User


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def find_all(self, page: int = 1, page_size: int = 20, search: str | None = None) -> tuple[list[User], int]: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None: ...

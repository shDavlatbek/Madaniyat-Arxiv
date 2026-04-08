from __future__ import annotations

import uuid
from datetime import datetime

from src.domain.shared.entity import Entity
from src.domain.user.value_objects import UserRole


class User(Entity):
    def __init__(
        self,
        username: str,
        name: str,
        hashed_password: str,
        role: UserRole = UserRole.USER,
        email: str | None = None,
        is_active: bool = True,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.username = username
        self.name = name
        self.email = email
        self.hashed_password = hashed_password
        self.role = role
        self.is_active = is_active

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def update(self, name: str | None = None, email: str | None = None, role: UserRole | None = None, is_active: bool | None = None) -> None:
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if role is not None:
            self.role = role
        if is_active is not None:
            self.is_active = is_active
        self.updated_at = datetime.now(__import__('datetime').timezone.utc)

    def change_password(self, new_hashed_password: str) -> None:
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.now(__import__('datetime').timezone.utc)

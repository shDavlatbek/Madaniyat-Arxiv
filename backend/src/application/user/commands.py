from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class CreateUserCommand:
    username: str
    name: str
    password: str
    role: str = "user"
    email: str | None = None
    is_active: bool = True


@dataclass
class UpdateUserCommand:
    user_id: uuid.UUID
    name: str | None = None
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None


@dataclass
class DeleteUserCommand:
    user_id: uuid.UUID


@dataclass
class ChangePasswordCommand:
    user_id: uuid.UUID
    new_password: str

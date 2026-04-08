from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=4)
    role: str = Field(default="user")
    email: str | None = None
    is_active: bool = True


class UpdateUserRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(min_length=4)


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    name: str
    email: str | None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int

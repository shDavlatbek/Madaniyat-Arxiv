from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class ListUsersQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None


@dataclass
class GetUserQuery:
    user_id: uuid.UUID

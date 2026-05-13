from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class ListDepartmentsQuery:
    search: str | None = None
    active_only: bool = False


@dataclass
class GetDepartmentQuery:
    department_id: uuid.UUID

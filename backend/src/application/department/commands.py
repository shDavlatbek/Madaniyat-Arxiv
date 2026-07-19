from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class CreateDepartmentCommand:
    name: str
    index_code: str | None = None
    description: str | None = None


@dataclass
class UpdateDepartmentCommand:
    department_id: uuid.UUID
    name: str | None = None
    index_code: str | None = None
    description: str | None = None


@dataclass
class DeleteDepartmentCommand:
    department_id: uuid.UUID


@dataclass
class ActivateDepartmentCommand:
    department_id: uuid.UUID


@dataclass
class DeactivateDepartmentCommand:
    department_id: uuid.UUID

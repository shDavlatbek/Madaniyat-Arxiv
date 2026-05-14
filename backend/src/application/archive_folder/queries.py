from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class ListArchiveFoldersQuery:
    year_id: int | None = None
    search: str | None = None


@dataclass
class GetArchiveFolderQuery:
    folder_id: uuid.UUID

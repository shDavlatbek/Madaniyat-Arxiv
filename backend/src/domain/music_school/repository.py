from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.music_school.entity import MusicSchool


class MusicSchoolRepository(ABC):
    @abstractmethod
    async def find_by_id(self, school_id: uuid.UUID) -> MusicSchool | None: ...

    @abstractmethod
    async def find_by_name(self, name: str) -> MusicSchool | None: ...

    @abstractmethod
    async def find_all(self, search: str | None = None) -> list[MusicSchool]: ...

    @abstractmethod
    async def save(self, school: MusicSchool) -> MusicSchool: ...

    @abstractmethod
    async def delete(self, school_id: uuid.UUID) -> None: ...

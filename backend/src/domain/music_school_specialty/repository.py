from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.music_school_specialty.entity import MusicSchoolSpecialty


class MusicSchoolSpecialtyRepository(ABC):
    @abstractmethod
    async def find_by_id(self, specialty_id: uuid.UUID) -> MusicSchoolSpecialty | None: ...

    @abstractmethod
    async def find_all_by_school(self, school_id: uuid.UUID) -> list[MusicSchoolSpecialty]: ...

    @abstractmethod
    async def find_by_school_and_name(self, school_id: uuid.UUID, name: str) -> MusicSchoolSpecialty | None: ...

    @abstractmethod
    async def save(self, specialty: MusicSchoolSpecialty) -> MusicSchoolSpecialty: ...

    @abstractmethod
    async def delete(self, specialty_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def has_documents_linked(self, specialty_id: uuid.UUID) -> bool: ...

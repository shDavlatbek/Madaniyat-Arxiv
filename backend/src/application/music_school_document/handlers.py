from __future__ import annotations

import uuid
from datetime import datetime

from src.domain.music_school_document.entity import MusicSchoolDocument
from src.domain.music_school_document.repository import MusicSchoolDocumentRepository
from src.domain.shared.errors import NotFoundError, ValidationError
from src.infrastructure.file_storage.local_storage import FileStorageService

from .commands import (
    CreateMusicSchoolDocumentCommand,
    DeleteMusicSchoolDocumentCommand,
    UpdateMusicSchoolDocumentCommand,
    UploadMusicSchoolDocumentFileCommand,
)
from .queries import GetMusicSchoolDocumentQuery, ListMusicSchoolDocumentsQuery


class MusicSchoolDocumentCommandHandler:
    def __init__(
        self,
        document_repo: MusicSchoolDocumentRepository,
        file_storage: FileStorageService,
    ):
        self._document_repo = document_repo
        self._file_storage = file_storage

    async def create(self, command: CreateMusicSchoolDocumentCommand) -> MusicSchoolDocument:
        # Validate graduation year matches given date year or similar if needed, or simple validation
        if command.graduation_year < 1900 or command.graduation_year > 2100:
            raise ValidationError("Graduation year must be between 1900 and 2100")

        document = MusicSchoolDocument(
            student_full_name=command.student_full_name,
            music_school_id=command.music_school_id,
            specialty_id=command.specialty_id,
            graduation_year=command.graduation_year,
            diploma_serial=command.diploma_serial,
            diploma_number=command.diploma_number,
            given_date=command.given_date,
            description=command.description,
            created_by=command.created_by,
        )
        return await self._document_repo.save(document)

    async def update(self, command: UpdateMusicSchoolDocumentCommand) -> MusicSchoolDocument:
        document = await self._document_repo.find_by_id(command.document_id)
        if not document:
            raise NotFoundError("MusicSchoolDocument", str(command.document_id))

        document.update(
            student_full_name=command.student_full_name,
            music_school_id=command.music_school_id,
            specialty_id=command.specialty_id,
            graduation_year=command.graduation_year,
            diploma_serial=command.diploma_serial,
            diploma_number=command.diploma_number,
            given_date=command.given_date,
            description=command.description,
        )
        return await self._document_repo.save(document)

    async def delete(self, command: DeleteMusicSchoolDocumentCommand) -> None:
        document = await self._document_repo.find_by_id(command.document_id)
        if document:
            if document.file_path:
                await self._file_storage.delete_file(document.file_path)
            await self._document_repo.delete(command.document_id)

    async def upload_file(self, command: UploadMusicSchoolDocumentFileCommand) -> MusicSchoolDocument:
        document = await self._document_repo.find_by_id(command.document_id)
        if not document:
            raise NotFoundError("MusicSchoolDocument", str(command.document_id))

        if document.file_path:
            await self._file_storage.delete_file(document.file_path)

        file_path = await self._file_storage.save_file(
            command.content,
            f"music_schools/{command.filename}",
            command.document_id,
        )
        document.set_file_path(file_path)
        return await self._document_repo.save(document)


class MusicSchoolDocumentQueryHandler:
    def __init__(self, document_repo: MusicSchoolDocumentRepository):
        self._document_repo = document_repo

    async def get_document(self, query: GetMusicSchoolDocumentQuery) -> MusicSchoolDocument:
        document = await self._document_repo.find_by_id(query.document_id)
        if not document:
            raise NotFoundError("MusicSchoolDocument", str(query.document_id))
        return document

    async def list_documents(self, query: ListMusicSchoolDocumentsQuery) -> tuple[list[MusicSchoolDocument], int]:
        return await self._document_repo.find_all(
            page=query.page,
            page_size=query.page_size,
            music_school_id=query.music_school_id,
            graduation_year=query.graduation_year,
            specialty_id=query.specialty_id,
            search=query.search,
        )

from __future__ import annotations

import uuid

from src.domain.category.repository import CategoryRepository
from src.domain.document.entity import Document
from src.domain.document.errors import DocumentNotFoundError
from src.domain.document.repository import DocumentRepository, DocumentSearchParams
from src.domain.document.value_objects import DocumentAttachment, DocumentFieldValue
from src.domain.shared.errors import ValidationError
from src.domain.year.repository import YearRepository
from src.infrastructure.file_storage.local_storage import FileStorageService

from .commands import CreateDocumentCommand, DeleteAttachmentCommand, DeleteDocumentCommand, UpdateDocumentCommand, UploadAttachmentCommand, UploadFileCommand
from .queries import GetDocumentQuery, ListDocumentsQuery


class DocumentCommandHandler:
    def __init__(
        self,
        document_repo: DocumentRepository,
        category_repo: CategoryRepository,
        year_repo: YearRepository,
        file_storage: FileStorageService,
    ):
        self._document_repo = document_repo
        self._category_repo = category_repo
        self._year_repo = year_repo
        self._file_storage = file_storage

    async def create(self, command: CreateDocumentCommand) -> Document:
        # Resolve year: command.year_id is the year VALUE (e.g. 2020), not the DB id
        year = await self._year_repo.find_by_value(command.year_id)
        if not year:
            raise ValidationError(f"{command.year_id} yil topilmadi")

        # Validate date falls within the year
        if command.date and command.date.year != year.value:
            raise ValidationError(
                f"Hujjat sanasi {year.value} yil oralig'ida bo'lishi kerak "
                f"({year.value}-01-01 dan {year.value}-12-31 gacha)"
            )

        # Build dynamic field values
        field_values = await self._build_field_values(command.category_id, command.dynamic_fields)

        document = Document(
            year_id=year.id,  # Use the DB id, not the year value
            category_id=command.category_id,
            title=command.title,
            document_number=command.document_number,
            date=command.date,
            short_desc=command.short_desc,
            pages=command.pages,
            signer=command.signer,
            archive_number=command.archive_number or None,
            person_id=command.person_id,
            created_by=command.created_by,
            field_values=field_values,
        )
        return await self._document_repo.save(document)

    async def update(self, command: UpdateDocumentCommand) -> Document:
        document = await self._document_repo.find_by_id(command.document_id)
        if not document:
            raise DocumentNotFoundError(str(command.document_id))

        # Validate date against document's year if date is being changed
        if command.date is not None:
            year = await self._year_repo.find_by_id(document.year_id)
            if year and command.date.year != year.value:
                raise ValidationError(
                    f"Hujjat sanasi {year.value} yil oralig'ida bo'lishi kerak "
                    f"({year.value}-01-01 dan {year.value}-12-31 gacha)"
                )

        document.update(
            category_id=command.category_id,
            title=command.title,
            document_number=command.document_number,
            date=command.date,
            short_desc=command.short_desc,
            pages=command.pages,
            signer=command.signer,
            archive_number=command.archive_number if command.archive_number else None,
            person_id=command.person_id,
        )

        if command.dynamic_fields is not None:
            field_values = await self._build_field_values(document.category_id, command.dynamic_fields)
            document.set_field_values(field_values)

        return await self._document_repo.save(document)

    async def delete(self, command: DeleteDocumentCommand) -> None:
        document = await self._document_repo.find_by_id(command.document_id)
        if document:
            if document.file_path:
                await self._file_storage.delete_file(document.file_path)
            for att in document.attachments:
                await self._file_storage.delete_file(att.file_path)
        await self._document_repo.delete(command.document_id)

    async def upload_file(self, command: UploadFileCommand) -> Document:
        document = await self._document_repo.find_by_id(command.document_id)
        if not document:
            raise DocumentNotFoundError(str(command.document_id))

        # Delete old file if exists
        if document.file_path:
            await self._file_storage.delete_file(document.file_path)

        file_path = await self._file_storage.save_file(command.content, command.filename, command.document_id)
        document.set_file_path(file_path)
        return await self._document_repo.save(document)

    async def upload_attachment(self, command: UploadAttachmentCommand) -> Document:
        document = await self._document_repo.find_by_id(command.document_id)
        if not document:
            raise DocumentNotFoundError(str(command.document_id))

        file_path = await self._file_storage.save_file(
            command.content, f"attachments/{command.filename}", command.document_id,
        )
        attachment = DocumentAttachment(
            document_id=document.id,
            file_path=file_path,
            original_filename=command.filename,
            sort_order=command.sort_order,
        )
        document.add_attachment(attachment)
        return await self._document_repo.save(document)

    async def delete_attachment(self, command: DeleteAttachmentCommand) -> Document:
        document = await self._document_repo.find_by_id(command.document_id)
        if not document:
            raise DocumentNotFoundError(str(command.document_id))

        attachment = next((a for a in document.attachments if a.id == command.attachment_id), None)
        if attachment:
            await self._file_storage.delete_file(attachment.file_path)
            document.remove_attachment(command.attachment_id)
        return await self._document_repo.save(document)

    async def _build_field_values(self, category_id: uuid.UUID, dynamic_fields: dict[str, str]) -> list[DocumentFieldValue]:
        if not dynamic_fields:
            return []
        fields = await self._category_repo.find_fields_by_category(category_id)
        field_map = {f.name: f for f in fields}
        result = []
        for name, value in dynamic_fields.items():
            field_def = field_map.get(name)
            if field_def:
                result.append(DocumentFieldValue(category_field_id=field_def.id, value=value))
        return result


class DocumentQueryHandler:
    def __init__(self, document_repo: DocumentRepository):
        self._document_repo = document_repo

    async def list_documents(self, query: ListDocumentsQuery) -> tuple[list[Document], int]:
        params = DocumentSearchParams(
            year_id=query.year_id,
            category_id=query.category_id,
            search=query.search,
            date_from=query.date_from,
            date_to=query.date_to,
            field_filters=query.field_filters if query.field_filters else None,
            page=query.page,
            page_size=query.page_size,
        )
        return await self._document_repo.search(params)

    async def get_document(self, query: GetDocumentQuery) -> Document:
        document = await self._document_repo.find_by_id(query.document_id)
        if not document:
            raise DocumentNotFoundError(str(query.document_id))
        return document

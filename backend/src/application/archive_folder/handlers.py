from __future__ import annotations

from src.domain.archive_folder.entity import ArchiveFolder
from src.domain.archive_folder.repository import ArchiveFolderRepository
from src.domain.shared.errors import NotFoundError, ValidationError

from .commands import CreateArchiveFolderCommand, DeleteArchiveFolderCommand, UpdateArchiveFolderCommand
from .queries import GetArchiveFolderQuery, ListArchiveFoldersQuery


class ArchiveFolderCommandHandler:
    def __init__(self, archive_folder_repo: ArchiveFolderRepository):
        self._repo = archive_folder_repo

    async def create(self, command: CreateArchiveFolderCommand) -> ArchiveFolder:
        existing = await self._repo.find_by_index_code(command.year_id, command.index_code.strip())
        if existing:
            raise ValidationError(
                f"Archive folder with index '{command.index_code}' already exists for this year"
            )
        folder = ArchiveFolder(
            index_code=command.index_code,
            title=command.title,
            department_id=command.department_id,
            article_number=command.article_number,
            list_number=command.list_number,
            note=command.note,
            retention_period_id=command.retention_period_id,
            total_sheets=command.total_sheets,
            start_date=command.start_date,
            end_date=command.end_date,
            year_id=command.year_id,
        )
        return await self._repo.save(folder)

    async def update(self, command: UpdateArchiveFolderCommand) -> ArchiveFolder:
        folder = await self._repo.find_by_id(command.folder_id)
        if not folder:
            raise NotFoundError("ArchiveFolder", str(command.folder_id))

        new_index = command.index_code.strip() if command.index_code is not None else folder.index_code
        new_year = command.year_id if command.year_id is not None else folder.year_id
        if (new_index, new_year) != (folder.index_code, folder.year_id):
            clash = await self._repo.find_by_index_code(new_year, new_index)
            if clash and clash.id != folder.id:
                raise ValidationError(
                    f"Archive folder with index '{new_index}' already exists for this year"
                )

        folder.update(
            index_code=command.index_code,
            title=command.title,
            department_id=command.department_id,
            article_number=command.article_number,
            list_number=command.list_number,
            note=command.note,
            retention_period_id=command.retention_period_id,
            total_sheets=command.total_sheets,
            start_date=command.start_date,
            end_date=command.end_date,
            year_id=command.year_id,
        )
        return await self._repo.save(folder)

    async def delete(self, command: DeleteArchiveFolderCommand) -> None:
        folder = await self._repo.find_by_id(command.folder_id)
        if not folder:
            raise NotFoundError("ArchiveFolder", str(command.folder_id))
        await self._repo.delete(command.folder_id)


class ArchiveFolderQueryHandler:
    def __init__(self, archive_folder_repo: ArchiveFolderRepository):
        self._repo = archive_folder_repo

    async def list_folders(self, query: ListArchiveFoldersQuery) -> list[tuple[ArchiveFolder, int, int]]:
        return await self._repo.find_all_with_counts(year_id=query.year_id, search=query.search)

    async def get_folder(self, query: GetArchiveFolderQuery) -> ArchiveFolder:
        folder = await self._repo.find_by_id(query.folder_id)
        if not folder:
            raise NotFoundError("ArchiveFolder", str(query.folder_id))
        return folder

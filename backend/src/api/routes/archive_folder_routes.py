import uuid

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_archive_folder_command_handler, get_archive_folder_query_handler
from src.api.middleware.auth import get_current_user, require_admin
from src.api.schemas.archive_folder import (
    ArchiveFolderListResponse,
    ArchiveFolderResponse,
    CreateArchiveFolderRequest,
    UpdateArchiveFolderRequest,
)
from src.application.archive_folder.commands import (
    CreateArchiveFolderCommand,
    DeleteArchiveFolderCommand,
    UpdateArchiveFolderCommand,
)
from src.application.archive_folder.handlers import ArchiveFolderCommandHandler, ArchiveFolderQueryHandler
from src.application.archive_folder.queries import GetArchiveFolderQuery, ListArchiveFoldersQuery
from src.domain.archive_folder.entity import ArchiveFolder
from src.domain.user.entity import User

router = APIRouter(prefix="/api/archive-folders", tags=["archive-folders"])


def _to_response(folder: ArchiveFolder, document_count: int = 0) -> ArchiveFolderResponse:
    return ArchiveFolderResponse(
        id=folder.id,
        index_code=folder.index_code,
        title=folder.title,
        retention_period=folder.retention_period,
        start_date=folder.start_date,
        end_date=folder.end_date,
        year_id=folder.year_id,
        document_count=document_count,
        created_at=folder.created_at,
        updated_at=folder.updated_at,
    )


@router.get("", response_model=ArchiveFolderListResponse)
async def list_archive_folders(
    year_id: int | None = Query(None),
    search: str | None = Query(None),
    handler: ArchiveFolderQueryHandler = Depends(get_archive_folder_query_handler),
    _: User = Depends(get_current_user),
):
    folders = await handler.list_folders(ListArchiveFoldersQuery(year_id=year_id, search=search))
    return ArchiveFolderListResponse(items=[_to_response(f, count) for f, count in folders])


@router.get("/{folder_id}", response_model=ArchiveFolderResponse)
async def get_archive_folder(
    folder_id: uuid.UUID,
    handler: ArchiveFolderQueryHandler = Depends(get_archive_folder_query_handler),
    _: User = Depends(get_current_user),
):
    folder = await handler.get_folder(GetArchiveFolderQuery(folder_id=folder_id))
    return _to_response(folder)


@router.post("", response_model=ArchiveFolderResponse, status_code=201)
async def create_archive_folder(
    request: CreateArchiveFolderRequest,
    handler: ArchiveFolderCommandHandler = Depends(get_archive_folder_command_handler),
    _: User = Depends(require_admin),
):
    folder = await handler.create(
        CreateArchiveFolderCommand(
            index_code=request.index_code,
            title=request.title,
            retention_period=request.retention_period,
            start_date=request.start_date,
            end_date=request.end_date,
            year_id=request.year_id,
        )
    )
    return _to_response(folder)


@router.put("/{folder_id}", response_model=ArchiveFolderResponse)
async def update_archive_folder(
    folder_id: uuid.UUID,
    request: UpdateArchiveFolderRequest,
    handler: ArchiveFolderCommandHandler = Depends(get_archive_folder_command_handler),
    _: User = Depends(require_admin),
):
    folder = await handler.update(
        UpdateArchiveFolderCommand(
            folder_id=folder_id,
            index_code=request.index_code,
            title=request.title,
            retention_period=request.retention_period,
            start_date=request.start_date,
            end_date=request.end_date,
            year_id=request.year_id,
        )
    )
    return _to_response(folder)


@router.delete("/{folder_id}", status_code=204)
async def delete_archive_folder(
    folder_id: uuid.UUID,
    handler: ArchiveFolderCommandHandler = Depends(get_archive_folder_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete(DeleteArchiveFolderCommand(folder_id=folder_id))

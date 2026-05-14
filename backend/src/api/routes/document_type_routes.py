import uuid

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_document_type_command_handler, get_document_type_query_handler
from src.api.middleware.auth import get_current_user, require_admin
from src.api.schemas.document_type import (
    CreateDocumentTypeRequest,
    DocumentTypeListResponse,
    DocumentTypeResponse,
    UpdateDocumentTypeRequest,
)
from src.application.document_type.commands import (
    CreateDocumentTypeCommand,
    DeleteDocumentTypeCommand,
    UpdateDocumentTypeCommand,
)
from src.application.document_type.handlers import DocumentTypeCommandHandler, DocumentTypeQueryHandler
from src.application.document_type.queries import GetDocumentTypeQuery, ListDocumentTypesQuery
from src.domain.document_type.entity import DocumentType
from src.domain.user.entity import User

router = APIRouter(prefix="/api/document-types", tags=["document-types"])


def _to_response(document_type: DocumentType) -> DocumentTypeResponse:
    return DocumentTypeResponse(
        id=document_type.id,
        name=document_type.name,
        created_at=document_type.created_at,
        updated_at=document_type.updated_at,
    )


@router.get("", response_model=DocumentTypeListResponse)
async def list_document_types(
    search: str | None = Query(None),
    handler: DocumentTypeQueryHandler = Depends(get_document_type_query_handler),
    _: User = Depends(get_current_user),
):
    document_types = await handler.list_document_types(ListDocumentTypesQuery(search=search))
    return DocumentTypeListResponse(items=[_to_response(d) for d in document_types])


@router.get("/{document_type_id}", response_model=DocumentTypeResponse)
async def get_document_type(
    document_type_id: uuid.UUID,
    handler: DocumentTypeQueryHandler = Depends(get_document_type_query_handler),
    _: User = Depends(get_current_user),
):
    document_type = await handler.get_document_type(
        GetDocumentTypeQuery(document_type_id=document_type_id)
    )
    return _to_response(document_type)


@router.post("", response_model=DocumentTypeResponse, status_code=201)
async def create_document_type(
    request: CreateDocumentTypeRequest,
    handler: DocumentTypeCommandHandler = Depends(get_document_type_command_handler),
    _: User = Depends(require_admin),
):
    document_type = await handler.create(CreateDocumentTypeCommand(name=request.name))
    return _to_response(document_type)


@router.put("/{document_type_id}", response_model=DocumentTypeResponse)
async def update_document_type(
    document_type_id: uuid.UUID,
    request: UpdateDocumentTypeRequest,
    handler: DocumentTypeCommandHandler = Depends(get_document_type_command_handler),
    _: User = Depends(require_admin),
):
    document_type = await handler.update(
        UpdateDocumentTypeCommand(document_type_id=document_type_id, name=request.name)
    )
    return _to_response(document_type)


@router.delete("/{document_type_id}", status_code=204)
async def delete_document_type(
    document_type_id: uuid.UUID,
    handler: DocumentTypeCommandHandler = Depends(get_document_type_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete(DeleteDocumentTypeCommand(document_type_id=document_type_id))

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse

from src.api.dependencies import get_document_command_handler, get_document_query_handler
from src.api.middleware.auth import get_current_user
from src.api.schemas.document import (
    AttachmentResponse,
    CreateDocumentRequest,
    DocumentFieldValueResponse,
    DocumentListResponse,
    DocumentResponse,
    UpdateDocumentRequest,
)
from src.application.document.commands import CreateDocumentCommand, DeleteAttachmentCommand, DeleteDocumentCommand, UpdateDocumentCommand, UploadAttachmentCommand, UploadFileCommand
from src.application.document.handlers import DocumentCommandHandler, DocumentQueryHandler
from src.application.document.queries import GetDocumentQuery, ListDocumentsQuery
from src.domain.document.entity import Document
from src.domain.document.value_objects import DocumentView
from src.domain.user.entity import User

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _to_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        year_id=doc.year_value or doc.year_id,
        category_id=doc.category_id,
        title=doc.title,
        document_number=doc.document_number,
        date=doc.date,
        short_desc=doc.short_desc,
        pages=doc.pages,
        file_path=doc.file_path,
        signer=doc.signer,
        archive_number=doc.archive_number,
        person_id=doc.person_id,
        person_name=doc.person_name,
        person_position=doc.person_position,
        created_by=doc.created_by,
        document_view=doc.document_view,
        archive_folder_id=doc.archive_folder_id,
        document_type_id=doc.document_type_id,
        document_type_name=doc.document_type_name,
        document_form=doc.document_form,
        sender=doc.sender,
        language=doc.language,
        related_document_number=doc.related_document_number,
        related_document_date=doc.related_document_date,
        received_date=doc.received_date,
        origin_organization=doc.origin_organization,
        sent_date=doc.sent_date,
        recipient_organization=doc.recipient_organization,
        applicant_full_name=doc.applicant_full_name,
        applicant_phone=doc.applicant_phone,
        region_id=doc.region_id,
        country_id=doc.country_id,
        reception_place_id=doc.reception_place_id,
        appeal_type_id=doc.appeal_type_id,
        person_type=doc.person_type,
        outgoing_number=doc.outgoing_number,
        outgoing_date=doc.outgoing_date,
        signed_by=doc.signed_by,
        note=doc.note,
        ocr_status=doc.ocr_status,
        ocr_completed_at=doc.ocr_completed_at,
        field_values=[
            DocumentFieldValueResponse(category_field_id=fv.category_field_id, value=fv.value)
            for fv in doc.field_values
        ],
        attachments=[
            AttachmentResponse(
                id=a.id, file_path=a.file_path, original_filename=a.original_filename,
                sort_order=a.sort_order, created_at=a.created_at,
                ocr_status=a.ocr_status, ocr_completed_at=a.ocr_completed_at,
            )
            for a in doc.attachments
        ],
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    year_id: int | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    search: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    field_filters: str | None = Query(None),
    document_view: DocumentView | None = Query(None),
    archive_folder_id: uuid.UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    handler: DocumentQueryHandler = Depends(get_document_query_handler),
    _: User = Depends(get_current_user),
):
    parsed_filters = {}
    if field_filters:
        try:
            parsed_filters = json.loads(field_filters)
        except json.JSONDecodeError:
            parsed_filters = {}

    docs, total = await handler.list_documents(ListDocumentsQuery(
        year_id=year_id,
        category_id=category_id,
        search=search,
        date_from=date_from,
        date_to=date_to,
        field_filters=parsed_filters,
        document_view=document_view,
        archive_folder_id=archive_folder_id,
        page=page,
        page_size=page_size,
    ))
    return DocumentListResponse(items=[_to_response(d) for d in docs], total=total, page=page, page_size=page_size)


@router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    request: CreateDocumentRequest,
    handler: DocumentCommandHandler = Depends(get_document_command_handler),
    current_user: User = Depends(get_current_user),
):
    doc = await handler.create(CreateDocumentCommand(
        year_id=request.year_id,
        category_id=request.category_id,
        title=request.title,
        document_number=request.document_number,
        date=request.date,
        short_desc=request.short_desc,
        pages=request.pages,
        signer=request.signer,
        archive_number=request.archive_number,
        person_id=request.person_id,
        created_by=current_user.id,
        dynamic_fields=request.dynamic_fields,
        document_view=request.document_view,
        archive_folder_id=request.archive_folder_id,
        document_type_id=request.document_type_id,
        document_form=request.document_form,
        sender=request.sender,
        language=request.language,
        related_document_number=request.related_document_number,
        related_document_date=request.related_document_date,
        received_date=request.received_date,
        origin_organization=request.origin_organization,
        sent_date=request.sent_date,
        recipient_organization=request.recipient_organization,
        applicant_full_name=request.applicant_full_name,
        applicant_phone=request.applicant_phone,
        region_id=request.region_id,
        country_id=request.country_id,
        reception_place_id=request.reception_place_id,
        appeal_type_id=request.appeal_type_id,
        person_type=request.person_type,
        outgoing_number=request.outgoing_number,
        outgoing_date=request.outgoing_date,
        signed_by=request.signed_by,
        note=request.note,
    ))
    return _to_response(doc)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    handler: DocumentQueryHandler = Depends(get_document_query_handler),
    _: User = Depends(get_current_user),
):
    doc = await handler.get_document(GetDocumentQuery(document_id=document_id))
    return _to_response(doc)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    request: UpdateDocumentRequest,
    handler: DocumentCommandHandler = Depends(get_document_command_handler),
    _: User = Depends(get_current_user),
):
    doc = await handler.update(UpdateDocumentCommand(
        document_id=document_id,
        category_id=request.category_id,
        title=request.title,
        document_number=request.document_number,
        date=request.date,
        short_desc=request.short_desc,
        pages=request.pages,
        signer=request.signer,
        archive_number=request.archive_number,
        person_id=request.person_id,
        dynamic_fields=request.dynamic_fields,
        document_view=request.document_view,
        archive_folder_id=request.archive_folder_id,
        document_type_id=request.document_type_id,
        document_form=request.document_form,
        sender=request.sender,
        language=request.language,
        related_document_number=request.related_document_number,
        related_document_date=request.related_document_date,
        received_date=request.received_date,
        origin_organization=request.origin_organization,
        sent_date=request.sent_date,
        recipient_organization=request.recipient_organization,
        applicant_full_name=request.applicant_full_name,
        applicant_phone=request.applicant_phone,
        region_id=request.region_id,
        country_id=request.country_id,
        reception_place_id=request.reception_place_id,
        appeal_type_id=request.appeal_type_id,
        person_type=request.person_type,
        outgoing_number=request.outgoing_number,
        outgoing_date=request.outgoing_date,
        signed_by=request.signed_by,
        note=request.note,
    ))
    return _to_response(doc)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    handler: DocumentCommandHandler = Depends(get_document_command_handler),
    _: User = Depends(get_current_user),
):
    await handler.delete(DeleteDocumentCommand(document_id=document_id))


@router.post("/{document_id}/file", response_model=DocumentResponse)
async def upload_file(
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    handler: DocumentCommandHandler = Depends(get_document_command_handler),
    _: User = Depends(get_current_user),
):
    content = await file.read()
    doc = await handler.upload_file(UploadFileCommand(
        document_id=document_id,
        filename=file.filename or "document",
        content=content,
    ))
    return _to_response(doc)


@router.get("/{document_id}/file")
async def download_file(
    document_id: uuid.UUID,
    handler: DocumentQueryHandler = Depends(get_document_query_handler),
    _: User = Depends(get_current_user),
):
    doc = await handler.get_document(GetDocumentQuery(document_id=document_id))
    if not doc.file_path:
        raise HTTPException(status_code=404, detail="No file attached")
    return FileResponse(doc.file_path)


@router.post("/{document_id}/attachments", response_model=DocumentResponse)
async def upload_attachment(
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    sort_order: int = Query(0),
    handler: DocumentCommandHandler = Depends(get_document_command_handler),
    _: User = Depends(get_current_user),
):
    content = await file.read()
    doc = await handler.upload_attachment(UploadAttachmentCommand(
        document_id=document_id,
        filename=file.filename or "attachment.pdf",
        content=content,
        sort_order=sort_order,
    ))
    return _to_response(doc)


@router.delete("/{document_id}/attachments/{attachment_id}", response_model=DocumentResponse)
async def delete_attachment(
    document_id: uuid.UUID,
    attachment_id: uuid.UUID,
    handler: DocumentCommandHandler = Depends(get_document_command_handler),
    _: User = Depends(get_current_user),
):
    doc = await handler.delete_attachment(DeleteAttachmentCommand(
        document_id=document_id,
        attachment_id=attachment_id,
    ))
    return _to_response(doc)


@router.get("/{document_id}/attachments/{attachment_id}")
async def download_attachment(
    document_id: uuid.UUID,
    attachment_id: uuid.UUID,
    handler: DocumentQueryHandler = Depends(get_document_query_handler),
    _: User = Depends(get_current_user),
):
    doc = await handler.get_document(GetDocumentQuery(document_id=document_id))
    attachment = next((a for a in doc.attachments if a.id == attachment_id), None)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return FileResponse(attachment.file_path)

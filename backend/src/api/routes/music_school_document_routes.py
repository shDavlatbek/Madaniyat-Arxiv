import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from elasticsearch import AsyncElasticsearch

from src.api.dependencies import (
    get_music_school_document_command_handler,
    get_music_school_document_query_handler,
)
from src.api.middleware.auth import require_music_school_or_admin
from src.api.schemas.music_school_document import (
    CreateMusicSchoolDocumentRequest,
    UpdateMusicSchoolDocumentRequest,
    MusicSchoolDocumentResponse,
    MusicSchoolDocumentListResponse,
    MusicSchoolSearchRequest,
    MusicSchoolSearchResponse,
    MusicSchoolSearchHit,
    MusicSchoolSearchHighlight,
)
from src.api.schemas.search import FacetBucket
from src.application.music_school_document.commands import (
    CreateMusicSchoolDocumentCommand,
    DeleteMusicSchoolDocumentCommand,
    UpdateMusicSchoolDocumentCommand,
    UploadMusicSchoolDocumentFileCommand,
)
from src.application.music_school_document.handlers import (
    MusicSchoolDocumentCommandHandler,
    MusicSchoolDocumentQueryHandler,
)
from src.application.music_school_document.queries import (
    GetMusicSchoolDocumentQuery,
    ListMusicSchoolDocumentsQuery,
)
from src.domain.music_school_document.entity import MusicSchoolDocument
from src.domain.user.entity import User
from src.domain.user.value_objects import UserRole
from src.infrastructure.jobs.arq_pool import get_arq_pool
from src.infrastructure.search.es_client import get_es
from src.infrastructure.search.music_index_template import ALIAS

router = APIRouter(prefix="/api/music-school-documents", tags=["music-school-documents"])
log = logging.getLogger("api.music_school_document_routes")


def _to_response(doc: MusicSchoolDocument) -> MusicSchoolDocumentResponse:
    return MusicSchoolDocumentResponse(
        id=doc.id,
        student_full_name=doc.student_full_name,
        music_school_id=doc.music_school_id,
        music_school_name=doc.music_school_name,
        specialty_id=doc.specialty_id,
        specialty=doc.specialty_name,
        graduation_year=doc.graduation_year,
        diploma_serial=doc.diploma_serial,
        diploma_number=doc.diploma_number,
        given_date=doc.given_date,
        description=doc.description,
        file_path=doc.file_path,
        ocr_status=doc.ocr_status,
        ocr_completed_at=doc.ocr_completed_at,
        created_by=doc.created_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


def _check_ownership(current_user: User, doc: MusicSchoolDocument) -> None:
    if current_user.role == UserRole.MUSIC_SCHOOL:
        if str(doc.music_school_id) != str(current_user.music_school_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ushbu hujjat sizning maktabingizga tegishli emas",
            )


@router.get("", response_model=MusicSchoolDocumentListResponse)
async def list_documents(
    music_school_id: uuid.UUID | None = Query(None),
    graduation_year: int | None = Query(None),
    specialty_id: uuid.UUID | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query_handler: MusicSchoolDocumentQueryHandler = Depends(get_music_school_document_query_handler),
    current_user: User = Depends(require_music_school_or_admin),
):
    # Multi-tenancy enforcement: if role is music_school, force filtering to their assigned school
    if current_user.role == UserRole.MUSIC_SCHOOL:
        music_school_id = current_user.music_school_id

    docs, total = await query_handler.list_documents(
        ListMusicSchoolDocumentsQuery(
            page=page,
            page_size=page_size,
            music_school_id=music_school_id,
            graduation_year=graduation_year,
            specialty_id=specialty_id,
            search=search,
        )
    )

    return MusicSchoolDocumentListResponse(
        items=[_to_response(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=MusicSchoolDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: CreateMusicSchoolDocumentRequest,
    command_handler: MusicSchoolDocumentCommandHandler = Depends(get_music_school_document_command_handler),
    current_user: User = Depends(require_music_school_or_admin),
):
    # Multi-tenancy enforcement: if role is music_school, ignore request school and lock to user school
    school_id = request.music_school_id
    if current_user.role == UserRole.MUSIC_SCHOOL:
        school_id = current_user.music_school_id

    doc = await command_handler.create(
        CreateMusicSchoolDocumentCommand(
            student_full_name=request.student_full_name,
            music_school_id=school_id,
            specialty_id=request.specialty_id,
            graduation_year=request.graduation_year,
            diploma_serial=request.diploma_serial,
            diploma_number=request.diploma_number,
            given_date=request.given_date,
            description=request.description,
            created_by=current_user.id,
        )
    )
    return _to_response(doc)


@router.get("/{document_id}", response_model=MusicSchoolDocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    query_handler: MusicSchoolDocumentQueryHandler = Depends(get_music_school_document_query_handler),
    current_user: User = Depends(require_music_school_or_admin),
):
    doc = await query_handler.get_document(GetMusicSchoolDocumentQuery(document_id=document_id))
    _check_ownership(current_user, doc)
    return _to_response(doc)


@router.put("/{document_id}", response_model=MusicSchoolDocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    request: UpdateMusicSchoolDocumentRequest,
    query_handler: MusicSchoolDocumentQueryHandler = Depends(get_music_school_document_query_handler),
    command_handler: MusicSchoolDocumentCommandHandler = Depends(get_music_school_document_command_handler),
    current_user: User = Depends(require_music_school_or_admin),
):
    doc = await query_handler.get_document(GetMusicSchoolDocumentQuery(document_id=document_id))
    _check_ownership(current_user, doc)

    school_id = request.music_school_id
    if current_user.role == UserRole.MUSIC_SCHOOL:
        school_id = current_user.music_school_id

    updated = await command_handler.update(
        UpdateMusicSchoolDocumentCommand(
            document_id=document_id,
            student_full_name=request.student_full_name,
            music_school_id=school_id,
            specialty_id=request.specialty_id,
            graduation_year=request.graduation_year,
            diploma_serial=request.diploma_serial,
            diploma_number=request.diploma_number,
            given_date=request.given_date,
            description=request.description,
        )
    )
    return _to_response(updated)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    query_handler: MusicSchoolDocumentQueryHandler = Depends(get_music_school_document_query_handler),
    command_handler: MusicSchoolDocumentCommandHandler = Depends(get_music_school_document_command_handler),
    current_user: User = Depends(require_music_school_or_admin),
):
    doc = await query_handler.get_document(GetMusicSchoolDocumentQuery(document_id=document_id))
    _check_ownership(current_user, doc)

    await command_handler.delete(DeleteMusicSchoolDocumentCommand(document_id=document_id))


@router.post("/{document_id}/file", response_model=MusicSchoolDocumentResponse)
async def upload_file(
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    query_handler: MusicSchoolDocumentQueryHandler = Depends(get_music_school_document_query_handler),
    command_handler: MusicSchoolDocumentCommandHandler = Depends(get_music_school_document_command_handler),
    current_user: User = Depends(require_music_school_or_admin),
):
    doc = await query_handler.get_document(GetMusicSchoolDocumentQuery(document_id=document_id))
    _check_ownership(current_user, doc)

    content = await file.read()
    updated = await command_handler.upload_file(
        UploadMusicSchoolDocumentFileCommand(
            document_id=document_id,
            content=content,
            filename=file.filename or f"diploma_{document_id}.pdf",
        )
    )

    # Fire-and-forget OCR job matching standard document upload
    try:
        pool = await get_arq_pool()
        await pool.enqueue_job("ocr_extract", str(document_id))
    except Exception as e:
        log.exception("Failed to enqueue OCR extract job: %s", e)

    return _to_response(updated)


@router.get("/{document_id}/file")
async def download_file(
    document_id: uuid.UUID,
    query_handler: MusicSchoolDocumentQueryHandler = Depends(get_music_school_document_query_handler),
    current_user: User = Depends(require_music_school_or_admin),
):
    doc = await query_handler.get_document(GetMusicSchoolDocumentQuery(document_id=document_id))
    _check_ownership(current_user, doc)

    if not doc.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hujjat fayli yuklanmagan",
        )
    return FileResponse(doc.file_path)


@router.post("/search", response_model=MusicSchoolSearchResponse)
async def search_documents(
    request: MusicSchoolSearchRequest,
    es: AsyncElasticsearch = Depends(get_es),
    current_user: User = Depends(require_music_school_or_admin),
):
    # Multi-tenancy enforcement: if role is music_school, lock search filters to their school
    if current_user.role == UserRole.MUSIC_SCHOOL:
        request.filters.music_school_id = [current_user.music_school_id]

    # Build the Elasticsearch query
    must: list[dict] = []
    if request.q:
        must.append({
            "multi_match": {
                "query": request.q,
                "fields": [
                    "student_full_name^3",
                    "music_school_name^2",
                    "specialty^2",
                    "diploma_serial",
                    "diploma_number",
                    "description",
                    "extracted_text",
                ],
                "type": "best_fields",
                "operator": "or",
            }
        })

    filter_clauses: list[dict] = []

    # Terms filters
    if request.filters.music_school_id:
        filter_clauses.append({"terms": {"music_school_id": [str(x) for x in request.filters.music_school_id]}})
    if request.filters.graduation_year:
        filter_clauses.append({"terms": {"graduation_year": request.filters.graduation_year}})
    if request.filters.specialty:
        filter_clauses.append({"terms": {"specialty.keyword": request.filters.specialty}})

    # Date range filters on given_date
    if request.filters.date_from or request.filters.date_to:
        rng: dict[str, str] = {}
        if request.filters.date_from:
            rng["gte"] = request.filters.date_from.isoformat()
        if request.filters.date_to:
            rng["lte"] = request.filters.date_to.isoformat()
        filter_clauses.append({"range": {"given_date": rng}})

    body: dict[str, Any] = {
        "from": max(0, (request.page - 1) * request.page_size),
        "size": request.page_size,
        "track_total_hits": True,
        "query": {
            "bool": {
                "must": must or [{"match_all": {}}],
                "filter": filter_clauses,
            }
        },
        "highlight": {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fragment_size": 150,
            "number_of_fragments": 3,
            "fields": {
                "student_full_name": {"number_of_fragments": 0},
                "specialty": {"number_of_fragments": 0},
                "description": {},
                "extracted_text": {},
            },
        },
    }

    # Sorting
    if request.sort == "date_desc":
        body["sort"] = [{"given_date": "desc"}]
    elif request.sort == "date_asc":
        body["sort"] = [{"given_date": "asc"}]

    # Facets
    if request.facets:
        body["aggs"] = {}
        for facet in request.facets:
            if facet == "music_school_id":
                body["aggs"]["music_school_id"] = {"terms": {"field": "music_school_id", "size": 50}}
            elif facet == "graduation_year":
                body["aggs"]["graduation_year"] = {"terms": {"field": "graduation_year", "size": 50}}
            elif facet == "specialty":
                body["aggs"]["specialty"] = {"terms": {"field": "specialty.keyword", "size": 50}}

    raw = await es.search(index=ALIAS, body=body)

    items: list[MusicSchoolSearchHit] = []
    for hit in raw["hits"]["hits"]:
        src = hit["_source"]
        hl = hit.get("highlight", {})
        items.append(
            MusicSchoolSearchHit(
                id=src["id"],
                score=hit.get("_score"),
                student_full_name=src.get("student_full_name"),
                music_school_id=src.get("music_school_id"),
                music_school_name=src.get("music_school_name"),
                specialty_id=src.get("specialty_id"),
                specialty=src.get("specialty"),
                graduation_year=src.get("graduation_year"),
                diploma_serial=src.get("diploma_serial"),
                diploma_number=src.get("diploma_number"),
                given_date=src.get("given_date"),
                description=src.get("description"),
                file_path=src.get("file_path"),
                ocr_status=src.get("ocr_status"),
                highlights=MusicSchoolSearchHighlight(
                    student_full_name=hl.get("student_full_name"),
                    specialty=hl.get("specialty"),
                    description=hl.get("description"),
                    extracted_text=hl.get("extracted_text"),
                ),
            )
        )

    facets: dict[str, list[FacetBucket]] = {}
    for agg_name, agg in raw.get("aggregations", {}).items():
        facets[agg_name] = [
            FacetBucket(value=str(b["key"]), count=b["doc_count"])
            for b in agg.get("buckets", [])
        ]

    return MusicSchoolSearchResponse(
        items=items,
        total=raw["hits"]["total"]["value"],
        page=request.page,
        page_size=request.page_size,
        took_ms=raw["took"],
        facets=facets,
    )

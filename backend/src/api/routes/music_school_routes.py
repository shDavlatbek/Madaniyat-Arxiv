import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_music_school_repository
from src.api.middleware.auth import require_admin, require_music_school_or_admin
from src.api.schemas.music_school import (
    CreateMusicSchoolRequest,
    MusicSchoolListResponse,
    MusicSchoolResponse,
    UpdateMusicSchoolRequest,
)
from src.domain.music_school.entity import MusicSchool
from src.domain.music_school.repository import MusicSchoolRepository
from src.domain.user.entity import User

router = APIRouter(prefix="/api/music-schools", tags=["music-schools"])


def _to_response(school: MusicSchool) -> MusicSchoolResponse:
    return MusicSchoolResponse(
        id=school.id,
        name=school.name,
        code=school.code,
        region=school.region,
        district=school.district,
        created_at=school.created_at,
        updated_at=school.updated_at,
    )


@router.get("", response_model=MusicSchoolListResponse)
async def list_music_schools(
    search: str | None = Query(None),
    repo: MusicSchoolRepository = Depends(get_music_school_repository),
    _: User = Depends(require_music_school_or_admin),
):
    schools = await repo.find_all(search=search)
    return MusicSchoolListResponse(items=[_to_response(s) for s in schools])


@router.get("/{school_id}", response_model=MusicSchoolResponse)
async def get_music_school(
    school_id: uuid.UUID,
    repo: MusicSchoolRepository = Depends(get_music_school_repository),
    _: User = Depends(require_music_school_or_admin),
):
    school = await repo.find_by_id(school_id)
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Musiqa maktabi topilmadi",
        )
    return _to_response(school)


@router.post("", response_model=MusicSchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_music_school(
    request: CreateMusicSchoolRequest,
    repo: MusicSchoolRepository = Depends(get_music_school_repository),
    _: User = Depends(require_admin),
):
    # Check if school name already exists
    existing = await repo.find_by_name(request.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bunday nomli musiqa maktabi allaqachon mavjud",
        )

    school = MusicSchool(name=request.name, code=request.code, region=request.region, district=request.district)
    saved = await repo.save(school)
    return _to_response(saved)


@router.put("/{school_id}", response_model=MusicSchoolResponse)
async def update_music_school(
    school_id: uuid.UUID,
    request: UpdateMusicSchoolRequest,
    repo: MusicSchoolRepository = Depends(get_music_school_repository),
    _: User = Depends(require_admin),
):
    school = await repo.find_by_id(school_id)
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Musiqa maktabi topilmadi",
        )

    school.update(name=request.name, code=request.code, region=request.region, district=request.district)
    saved = await repo.save(school)
    return _to_response(saved)


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_music_school(
    school_id: uuid.UUID,
    repo: MusicSchoolRepository = Depends(get_music_school_repository),
    _: User = Depends(require_admin),
):
    school = await repo.find_by_id(school_id)
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Musiqa maktabi topilmadi",
        )
    await repo.delete(school_id)

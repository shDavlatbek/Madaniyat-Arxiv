import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_music_school_specialty_repository
from src.api.middleware.auth import require_music_school_or_admin
from src.api.schemas.music_school_document import (
    MusicSchoolSpecialtyRequest,
    MusicSchoolSpecialtyResponse,
    MusicSchoolSpecialtyImportRequest,
)
from src.domain.music_school_specialty.entity import MusicSchoolSpecialty
from src.domain.music_school_specialty.repository import MusicSchoolSpecialtyRepository
from src.domain.user.entity import User
from src.domain.user.value_objects import UserRole
from src.domain.shared.errors import ValidationError

router = APIRouter(prefix="/api/music-schools/{school_id}/specialties", tags=["music-school-specialties"])
log = logging.getLogger("api.music_school_specialty_routes")


def _check_school_access(current_user: User, school_id: uuid.UUID) -> None:
    if current_user.role == UserRole.MUSIC_SCHOOL:
        if str(current_user.music_school_id) != str(school_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ushbu maktab ma'lumotlarini boshqarish huquqingiz yo'q",
            )


def _to_response(specialty: MusicSchoolSpecialty) -> MusicSchoolSpecialtyResponse:
    return MusicSchoolSpecialtyResponse(
        id=specialty.id,
        music_school_id=specialty.music_school_id,
        name=specialty.name,
        created_at=specialty.created_at,
        updated_at=specialty.updated_at,
    )


@router.get("", response_model=list[MusicSchoolSpecialtyResponse])
async def list_specialties(
    school_id: uuid.UUID,
    repo: MusicSchoolSpecialtyRepository = Depends(get_music_school_specialty_repository),
    current_user: User = Depends(require_music_school_or_admin),
):
    _check_school_access(current_user, school_id)
    specialties = await repo.find_all_by_school(school_id)
    return [_to_response(s) for s in specialties]


@router.post("", response_model=MusicSchoolSpecialtyResponse, status_code=status.HTTP_201_CREATED)
async def create_specialty(
    school_id: uuid.UUID,
    request: MusicSchoolSpecialtyRequest,
    repo: MusicSchoolSpecialtyRepository = Depends(get_music_school_specialty_repository),
    current_user: User = Depends(require_music_school_or_admin),
):
    _check_school_access(current_user, school_id)
    
    # Check duplicate
    existing = await repo.find_by_school_and_name(school_id, request.name)
    if existing:
        raise ValidationError(f"'{request.name}' nomli mutaxassislik ushbu maktabda allaqachon mavjud")
        
    specialty = MusicSchoolSpecialty(
        music_school_id=school_id,
        name=request.name
    )
    saved = await repo.save(specialty)
    return _to_response(saved)


@router.delete("/{specialty_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specialty(
    school_id: uuid.UUID,
    specialty_id: uuid.UUID,
    repo: MusicSchoolSpecialtyRepository = Depends(get_music_school_specialty_repository),
    current_user: User = Depends(require_music_school_or_admin),
):
    _check_school_access(current_user, school_id)
    
    specialty = await repo.find_by_id(specialty_id)
    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mutaxassislik topilmadi",
        )
        
    if str(specialty.music_school_id) != str(school_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mutaxassislik ushbu maktabga tegishli emas",
        )
        
    # Check if documents are linked
    if await repo.has_documents_linked(specialty_id):
        raise ValidationError("Ushbu mutaxassislikka tegishli hujjatlar mavjud, uni o'chirish mumkin emas")
        
    await repo.delete(specialty_id)


@router.post("/import", response_model=list[MusicSchoolSpecialtyResponse])
async def import_specialties(
    school_id: uuid.UUID,
    request: MusicSchoolSpecialtyImportRequest,
    repo: MusicSchoolSpecialtyRepository = Depends(get_music_school_specialty_repository),
    current_user: User = Depends(require_music_school_or_admin),
):
    _check_school_access(current_user, school_id)
    
    if str(request.source_school_id) == str(school_id):
        raise ValidationError("O'z maktabingizdan nusxa ko'chirib bo'lmaydi")
        
    imported = []
    for spec_id in request.specialty_ids:
        spec = await repo.find_by_id(spec_id)
        if not spec:
            continue
            
        if str(spec.music_school_id) != str(request.source_school_id):
            continue
            
        # Check duplicate
        existing = await repo.find_by_school_and_name(school_id, spec.name)
        if not existing:
            new_spec = MusicSchoolSpecialty(
                music_school_id=school_id,
                name=spec.name
            )
            saved = await repo.save(new_spec)
            imported.append(saved)
            
    return [_to_response(s) for s in imported]

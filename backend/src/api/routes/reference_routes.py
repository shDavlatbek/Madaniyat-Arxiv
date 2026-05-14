from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_reference_repository
from src.api.middleware.auth import get_current_user
from src.api.schemas.reference import (
    AppealTypeListResponse,
    AppealTypeResponse,
    ReceptionPlaceListResponse,
    ReceptionPlaceResponse,
    RegionListResponse,
    RegionResponse,
)
from src.domain.user.entity import User
from src.infrastructure.persistence.repositories.reference_repository import (
    SqlAlchemyReferenceRepository,
)

router = APIRouter(prefix="/api", tags=["references"])


@router.get("/regions", response_model=RegionListResponse)
async def list_regions(
    type: str | None = Query(None, description="LOCAL yoki ABROAD bo'yicha filtr"),
    repo: SqlAlchemyReferenceRepository = Depends(get_reference_repository),
    _: User = Depends(get_current_user),
):
    regions = await repo.list_regions(region_type=type)
    return RegionListResponse(
        items=[RegionResponse(id=r.id, name=r.name, type=r.type) for r in regions]
    )


@router.get("/reception-places", response_model=ReceptionPlaceListResponse)
async def list_reception_places(
    repo: SqlAlchemyReferenceRepository = Depends(get_reference_repository),
    _: User = Depends(get_current_user),
):
    places = await repo.list_reception_places()
    return ReceptionPlaceListResponse(
        items=[ReceptionPlaceResponse(id=p.id, name=p.name) for p in places]
    )


@router.get("/appeal-types", response_model=AppealTypeListResponse)
async def list_appeal_types(
    repo: SqlAlchemyReferenceRepository = Depends(get_reference_repository),
    _: User = Depends(get_current_user),
):
    types = await repo.list_appeal_types()
    return AppealTypeListResponse(
        items=[AppealTypeResponse(id=t.id, name=t.name) for t in types]
    )

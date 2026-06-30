from fastapi import APIRouter, Depends, Query
import json
from pathlib import Path
from typing import Any

from src.api.dependencies import get_reference_repository
from src.api.middleware.auth import get_current_user
from src.api.schemas.reference import (
    AppealTypeListResponse,
    AppealTypeResponse,
    ReceptionPlaceListResponse,
    ReceptionPlaceResponse,
    RegionListResponse,
    RegionResponse,
    RetentionPeriodListResponse,
    RetentionPeriodResponse,
)
from src.domain.user.entity import User
from src.infrastructure.persistence.repositories.reference_repository import (
    SqlAlchemyReferenceRepository,
)

router = APIRouter(prefix="/api", tags=["references"])

# Resolve the path to the data files
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "infrastructure" / "persistence" / "data"
REGIONS_PATH = DATA_DIR / "regions.json"
DISTRICTS_PATH = DATA_DIR / "districts.json"

_cached_regions: list[dict[str, Any]] | None = None
_cached_districts: list[dict[str, Any]] | None = None

def get_regions_data() -> list[dict[str, Any]]:
    global _cached_regions
    if _cached_regions is None:
        if REGIONS_PATH.exists():
            with open(REGIONS_PATH, encoding="utf-8-sig") as f:
                _cached_regions = json.load(f)
        else:
            _cached_regions = []
    return _cached_regions

def get_districts_data() -> list[dict[str, Any]]:
    global _cached_districts
    if _cached_districts is None:
        if DISTRICTS_PATH.exists():
            with open(DISTRICTS_PATH, encoding="utf-8-sig") as f:
                _cached_districts = json.load(f)
        else:
            _cached_districts = []
    return _cached_districts


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


@router.get("/retention-periods", response_model=RetentionPeriodListResponse)
async def list_retention_periods(
    repo: SqlAlchemyReferenceRepository = Depends(get_reference_repository),
    _: User = Depends(get_current_user),
):
    periods = await repo.list_retention_periods()
    return RetentionPeriodListResponse(
        items=[RetentionPeriodResponse(id=p.id, name=p.name) for p in periods]
    )


@router.get("/locations/regions")
async def list_location_regions(_: User = Depends(get_current_user)):
    return get_regions_data()


@router.get("/locations/districts")
async def list_location_districts(_: User = Depends(get_current_user)):
    return get_districts_data()


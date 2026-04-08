from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_year_command_handler, get_year_query_handler
from src.api.middleware.auth import get_current_user, require_admin
from src.api.schemas.year import CreateYearRequest, UpdateYearRequest, YearListResponse, YearResponse
from src.application.year.commands import CreateYearCommand, DeleteYearCommand, UpdateYearCommand
from src.application.year.handlers import YearCommandHandler, YearQueryHandler
from src.application.year.queries import ListYearsQuery
from src.domain.user.entity import User
from src.domain.year.entity import Year

router = APIRouter(prefix="/api/years", tags=["years"])


def _to_response(year: Year) -> YearResponse:
    return YearResponse(id=year.id, value=year.value, is_active=year.is_active, created_at=year.created_at, updated_at=year.updated_at)


@router.get("", response_model=YearListResponse)
async def list_years(
    active_only: bool = Query(True),
    handler: YearQueryHandler = Depends(get_year_query_handler),
    _: User = Depends(get_current_user),
):
    years = await handler.list_years(ListYearsQuery(active_only=active_only))
    return YearListResponse(items=[_to_response(y) for y in years])


@router.post("", response_model=YearResponse, status_code=201)
async def create_year(
    request: CreateYearRequest,
    handler: YearCommandHandler = Depends(get_year_command_handler),
    _: User = Depends(require_admin),
):
    year = await handler.create(CreateYearCommand(value=request.value, is_active=request.is_active))
    return _to_response(year)


@router.put("/{year_id}", response_model=YearResponse)
async def update_year(
    year_id: int,
    request: UpdateYearRequest,
    handler: YearCommandHandler = Depends(get_year_command_handler),
    _: User = Depends(require_admin),
):
    year = await handler.update(UpdateYearCommand(year_id=year_id, value=request.value, is_active=request.is_active))
    return _to_response(year)


@router.delete("/{year_id}", status_code=204)
async def delete_year(
    year_id: int,
    handler: YearCommandHandler = Depends(get_year_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete(DeleteYearCommand(year_id=year_id))

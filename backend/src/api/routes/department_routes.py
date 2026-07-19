import uuid

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_department_command_handler, get_department_query_handler
from src.api.middleware.auth import get_current_user, require_admin
from src.api.schemas.department import (
    CreateDepartmentRequest,
    DepartmentListResponse,
    DepartmentResponse,
    UpdateDepartmentRequest,
)
from src.application.department.commands import (
    ActivateDepartmentCommand,
    CreateDepartmentCommand,
    DeactivateDepartmentCommand,
    DeleteDepartmentCommand,
    UpdateDepartmentCommand,
)
from src.application.department.handlers import DepartmentCommandHandler, DepartmentQueryHandler
from src.application.department.queries import GetDepartmentQuery, ListDepartmentsQuery
from src.domain.department.entity import Department
from src.domain.user.entity import User

router = APIRouter(prefix="/api/departments", tags=["departments"])


def _to_response(department: Department) -> DepartmentResponse:
    return DepartmentResponse(
        id=department.id,
        name=department.name,
        index_code=department.index_code,
        description=department.description,
        is_active=department.is_active,
        created_at=department.created_at,
        updated_at=department.updated_at,
    )


@router.get("", response_model=DepartmentListResponse)
async def list_departments(
    search: str | None = Query(None),
    active_only: bool = Query(False),
    handler: DepartmentQueryHandler = Depends(get_department_query_handler),
    _: User = Depends(get_current_user),
):
    departments = await handler.list_departments(
        ListDepartmentsQuery(search=search, active_only=active_only)
    )
    return DepartmentListResponse(items=[_to_response(d) for d in departments])


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: uuid.UUID,
    handler: DepartmentQueryHandler = Depends(get_department_query_handler),
    _: User = Depends(get_current_user),
):
    department = await handler.get_department(GetDepartmentQuery(department_id=department_id))
    return _to_response(department)


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    request: CreateDepartmentRequest,
    handler: DepartmentCommandHandler = Depends(get_department_command_handler),
    _: User = Depends(require_admin),
):
    department = await handler.create(
        CreateDepartmentCommand(
            name=request.name,
            index_code=request.index_code,
            description=request.description,
        )
    )
    return _to_response(department)


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: uuid.UUID,
    request: UpdateDepartmentRequest,
    handler: DepartmentCommandHandler = Depends(get_department_command_handler),
    _: User = Depends(require_admin),
):
    department = await handler.update(
        UpdateDepartmentCommand(
            department_id=department_id,
            name=request.name,
            index_code=request.index_code,
            description=request.description,
        )
    )
    return _to_response(department)


@router.delete("/{department_id}", status_code=204)
async def delete_department(
    department_id: uuid.UUID,
    handler: DepartmentCommandHandler = Depends(get_department_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete(DeleteDepartmentCommand(department_id=department_id))


@router.post("/{department_id}/activate", response_model=DepartmentResponse)
async def activate_department(
    department_id: uuid.UUID,
    handler: DepartmentCommandHandler = Depends(get_department_command_handler),
    _: User = Depends(require_admin),
):
    department = await handler.activate(ActivateDepartmentCommand(department_id=department_id))
    return _to_response(department)


@router.post("/{department_id}/deactivate", response_model=DepartmentResponse)
async def deactivate_department(
    department_id: uuid.UUID,
    handler: DepartmentCommandHandler = Depends(get_department_command_handler),
    _: User = Depends(require_admin),
):
    department = await handler.deactivate(DeactivateDepartmentCommand(department_id=department_id))
    return _to_response(department)

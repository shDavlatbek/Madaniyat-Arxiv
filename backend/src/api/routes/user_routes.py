import uuid

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_user_command_handler, get_user_query_handler
from src.api.middleware.auth import get_current_user, require_admin
from src.api.schemas.user import (
    ChangePasswordRequest,
    CreateUserRequest,
    UpdateUserRequest,
    UserListResponse,
    UserResponse,
)
from src.application.user.commands import ChangePasswordCommand, CreateUserCommand, DeleteUserCommand, UpdateUserCommand
from src.application.user.handlers import UserCommandHandler, UserQueryHandler
from src.application.user.queries import GetUserQuery, ListUsersQuery
from src.domain.user.entity import User

router = APIRouter(prefix="/api/users", tags=["users"])


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    handler: UserQueryHandler = Depends(get_user_query_handler),
    _: User = Depends(require_admin),
):
    users, total = await handler.list_users(ListUsersQuery(page=page, page_size=page_size, search=search))
    return UserListResponse(items=[_to_response(u) for u in users], total=total, page=page, page_size=page_size)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    request: CreateUserRequest,
    handler: UserCommandHandler = Depends(get_user_command_handler),
    _: User = Depends(require_admin),
):
    user = await handler.create(CreateUserCommand(
        username=request.username,
        name=request.name,
        password=request.password,
        role=request.role,
        email=request.email,
        is_active=request.is_active,
    ))
    return _to_response(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    handler: UserQueryHandler = Depends(get_user_query_handler),
    _: User = Depends(get_current_user),
):
    user = await handler.get_user(GetUserQuery(user_id=user_id))
    return _to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    request: UpdateUserRequest,
    handler: UserCommandHandler = Depends(get_user_command_handler),
    _: User = Depends(require_admin),
):
    user = await handler.update(UpdateUserCommand(
        user_id=user_id,
        name=request.name,
        email=request.email,
        role=request.role,
        is_active=request.is_active,
    ))
    return _to_response(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    handler: UserCommandHandler = Depends(get_user_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete(DeleteUserCommand(user_id=user_id))


@router.put("/{user_id}/password", response_model=UserResponse)
async def change_password(
    user_id: uuid.UUID,
    request: ChangePasswordRequest,
    handler: UserCommandHandler = Depends(get_user_command_handler),
    _: User = Depends(get_current_user),
):
    user = await handler.change_password(ChangePasswordCommand(user_id=user_id, new_password=request.new_password))
    return _to_response(user)

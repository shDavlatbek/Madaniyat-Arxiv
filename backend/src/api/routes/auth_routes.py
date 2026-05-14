from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.api.schemas.user import UserResponse
from src.domain.user.entity import User
from src.infrastructure.auth.jwt_service import create_access_token
from src.infrastructure.auth.password_service import verify_password
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories.user_repository import SqlAlchemyUserRepository

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    repo = SqlAlchemyUserRepository(session)
    user = await repo.find_by_username(request.username)

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Noto'g'ri foydalanuvchi nomi yoki parol")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Foydalanuvchi faol emas")

    token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=token,
        user=_user_response(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return _user_response(current_user)


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        department_id=user.department_id,
        department_name=user.department_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

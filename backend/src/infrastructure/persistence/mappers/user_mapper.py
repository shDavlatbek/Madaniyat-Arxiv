from src.domain.user.entity import User
from src.domain.user.value_objects import UserRole
from src.infrastructure.persistence.models import UserModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            name=model.name,
            email=model.email,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            name=entity.name,
            email=entity.email,
            hashed_password=entity.hashed_password,
            role=entity.role.value,
            is_active=entity.is_active,
        )

    @staticmethod
    def update_model(model: UserModel, entity: User) -> None:
        model.username = entity.username
        model.name = entity.name
        model.email = entity.email
        model.hashed_password = entity.hashed_password
        model.role = entity.role.value
        model.is_active = entity.is_active

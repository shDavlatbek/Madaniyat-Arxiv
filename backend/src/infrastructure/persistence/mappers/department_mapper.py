from src.domain.department.entity import Department
from src.infrastructure.persistence.models import DepartmentModel


class DepartmentMapper:
    @staticmethod
    def to_domain(model: DepartmentModel) -> Department:
        return Department(
            id=model.id,
            name=model.name,
            index_code=model.index_code,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Department) -> DepartmentModel:
        return DepartmentModel(
            id=entity.id,
            name=entity.name,
            index_code=entity.index_code,
            description=entity.description,
            is_active=entity.is_active,
        )

    @staticmethod
    def update_model(model: DepartmentModel, entity: Department) -> None:
        model.name = entity.name
        model.index_code = entity.index_code
        model.description = entity.description
        model.is_active = entity.is_active

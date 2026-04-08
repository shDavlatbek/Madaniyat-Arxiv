from src.domain.year.entity import Year
from src.infrastructure.persistence.models import YearModel


class YearMapper:
    @staticmethod
    def to_domain(model: YearModel) -> Year:
        return Year(
            id=model.id,
            value=model.value,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Year) -> YearModel:
        model = YearModel(
            value=entity.value,
            is_active=entity.is_active,
        )
        if entity.id is not None:
            model.id = entity.id
        return model

    @staticmethod
    def update_model(model: YearModel, entity: Year) -> None:
        model.value = entity.value
        model.is_active = entity.is_active

from src.domain.music_school.entity import MusicSchool
from src.infrastructure.persistence.models import MusicSchoolModel


class MusicSchoolMapper:
    @staticmethod
    def to_domain(model: MusicSchoolModel) -> MusicSchool:
        return MusicSchool(
            id=model.id,
            name=model.name,
            code=model.code,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: MusicSchool) -> MusicSchoolModel:
        return MusicSchoolModel(
            id=entity.id,
            name=entity.name,
            code=entity.code,
        )

    @staticmethod
    def update_model(model: MusicSchoolModel, entity: MusicSchool) -> None:
        model.name = entity.name
        model.code = entity.code

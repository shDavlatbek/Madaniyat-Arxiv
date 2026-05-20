from src.domain.music_school_specialty.entity import MusicSchoolSpecialty
from src.infrastructure.persistence.models import MusicSchoolSpecialtyModel


class MusicSchoolSpecialtyMapper:
    @staticmethod
    def to_domain(model: MusicSchoolSpecialtyModel) -> MusicSchoolSpecialty:
        return MusicSchoolSpecialty(
            id=model.id,
            music_school_id=model.music_school_id,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: MusicSchoolSpecialty) -> MusicSchoolSpecialtyModel:
        return MusicSchoolSpecialtyModel(
            id=entity.id,
            music_school_id=entity.music_school_id,
            name=entity.name,
        )

    @staticmethod
    def update_model(model: MusicSchoolSpecialtyModel, entity: MusicSchool) -> None:
        model.name = entity.name
        model.music_school_id = entity.music_school_id

from src.domain.person.entity import Person, PersonTenure
from src.infrastructure.persistence.models import PersonModel, PersonTenureModel


class PersonMapper:
    @staticmethod
    def to_domain(model: PersonModel) -> Person:
        tenures = [
            PersonTenure(
                id=t.id,
                person_id=t.person_id,
                position=t.position,
                start_date=t.start_date,
                end_date=t.end_date,
                created_at=t.created_at,
            )
            for t in model.tenures
        ] if model.tenures else []

        return Person(
            id=model.id,
            full_name=model.full_name,
            tenures=tenures,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Person) -> PersonModel:
        return PersonModel(
            id=entity.id,
            full_name=entity.full_name,
        )

    @staticmethod
    def update_model(model: PersonModel, entity: Person) -> None:
        model.full_name = entity.full_name

    @staticmethod
    def tenure_to_model(tenure: PersonTenure) -> PersonTenureModel:
        return PersonTenureModel(
            id=tenure.id,
            person_id=tenure.person_id,
            position=tenure.position,
            start_date=tenure.start_date,
            end_date=tenure.end_date,
        )

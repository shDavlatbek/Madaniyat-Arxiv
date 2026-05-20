from src.domain.music_school_document.entity import MusicSchoolDocument
from src.infrastructure.persistence.models import MusicSchoolDocumentModel


class MusicSchoolDocumentMapper:
    @staticmethod
    def to_domain(model: MusicSchoolDocumentModel) -> MusicSchoolDocument:
        return MusicSchoolDocument(
            id=model.id,
            student_full_name=model.student_full_name,
            music_school_id=model.music_school_id,
            music_school_name=model.music_school.name if model.music_school else None,
            specialty_id=model.specialty_id,
            specialty_name=model.specialty.name if model.specialty else None,
            graduation_year=model.graduation_year,
            diploma_serial=model.diploma_serial,
            diploma_number=model.diploma_number,
            given_date=model.given_date,
            description=model.description,
            file_path=model.file_path,
            extracted_text=model.extracted_text,
            ocr_status=model.ocr_status,
            ocr_completed_at=model.ocr_completed_at,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: MusicSchoolDocument) -> MusicSchoolDocumentModel:
        return MusicSchoolDocumentModel(
            id=entity.id,
            student_full_name=entity.student_full_name,
            music_school_id=entity.music_school_id,
            specialty_id=entity.specialty_id,
            graduation_year=entity.graduation_year,
            diploma_serial=entity.diploma_serial,
            diploma_number=entity.diploma_number,
            given_date=entity.given_date,
            description=entity.description,
            file_path=entity.file_path,
            extracted_text=entity.extracted_text,
            ocr_status=entity.ocr_status,
            ocr_completed_at=entity.ocr_completed_at,
            created_by=entity.created_by,
        )

    @staticmethod
    def update_model(model: MusicSchoolDocumentModel, entity: MusicSchoolDocument) -> None:
        model.student_full_name = entity.student_full_name
        model.music_school_id = entity.music_school_id
        model.specialty_id = entity.specialty_id
        model.graduation_year = entity.graduation_year
        model.diploma_serial = entity.diploma_serial
        model.diploma_number = entity.diploma_number
        model.given_date = entity.given_date
        model.description = entity.description
        model.file_path = entity.file_path
        model.extracted_text = entity.extracted_text
        model.ocr_status = entity.ocr_status
        model.ocr_completed_at = entity.ocr_completed_at
        model.created_by = entity.created_by

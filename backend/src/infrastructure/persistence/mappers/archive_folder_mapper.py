from src.domain.archive_folder.entity import ArchiveFolder
from src.infrastructure.persistence.models import ArchiveFolderModel


class ArchiveFolderMapper:
    @staticmethod
    def to_domain(model: ArchiveFolderModel) -> ArchiveFolder:
        return ArchiveFolder(
            id=model.id,
            index_code=model.index_code,
            title=model.title,
            retention_period_id=model.retention_period_id,
            retention_period_name=model.retention_period.name if model.retention_period else None,
            start_date=model.start_date,
            end_date=model.end_date,
            year_id=model.year_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: ArchiveFolder) -> ArchiveFolderModel:
        return ArchiveFolderModel(
            id=entity.id,
            index_code=entity.index_code,
            title=entity.title,
            retention_period_id=entity.retention_period_id,
            start_date=entity.start_date,
            end_date=entity.end_date,
            year_id=entity.year_id,
        )

    @staticmethod
    def update_model(model: ArchiveFolderModel, entity: ArchiveFolder) -> None:
        model.index_code = entity.index_code
        model.title = entity.title
        model.retention_period_id = entity.retention_period_id
        model.start_date = entity.start_date
        model.end_date = entity.end_date
        model.year_id = entity.year_id

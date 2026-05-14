from src.domain.document_type.entity import DocumentType
from src.infrastructure.persistence.models import DocumentTypeModel


class DocumentTypeMapper:
    @staticmethod
    def to_domain(model: DocumentTypeModel) -> DocumentType:
        return DocumentType(
            id=model.id,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: DocumentType) -> DocumentTypeModel:
        return DocumentTypeModel(id=entity.id, name=entity.name)

    @staticmethod
    def update_model(model: DocumentTypeModel, entity: DocumentType) -> None:
        model.name = entity.name

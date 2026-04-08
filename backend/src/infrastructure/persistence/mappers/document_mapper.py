import uuid

from src.domain.document.entity import Document
from src.domain.document.value_objects import DocumentFieldValue
from src.infrastructure.persistence.models import DocumentFieldValueModel, DocumentModel


class DocumentMapper:
    @staticmethod
    def to_domain(model: DocumentModel) -> Document:
        field_values = [
            DocumentFieldValue(
                id=fv.id,
                category_field_id=fv.category_field_id,
                value=fv.value,
            )
            for fv in model.field_values
        ] if model.field_values else []

        return Document(
            id=model.id,
            year_id=model.year_id,
            category_id=model.category_id,
            title=model.title,
            document_number=model.document_number,
            date=model.date,
            short_desc=model.short_desc,
            target=model.target,
            pages=model.pages,
            file_path=model.file_path,
            signer=model.signer,
            created_by=model.created_by,
            field_values=field_values,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        model = DocumentModel(
            id=entity.id,
            year_id=entity.year_id,
            category_id=entity.category_id,
            title=entity.title,
            document_number=entity.document_number,
            date=entity.date,
            short_desc=entity.short_desc,
            target=entity.target,
            pages=entity.pages,
            file_path=entity.file_path,
            signer=entity.signer,
            created_by=entity.created_by,
        )
        return model

    @staticmethod
    def update_model(model: DocumentModel, entity: Document) -> None:
        model.title = entity.title
        model.document_number = entity.document_number
        model.date = entity.date
        model.short_desc = entity.short_desc
        model.target = entity.target
        model.pages = entity.pages
        model.file_path = entity.file_path
        model.signer = entity.signer

    @staticmethod
    def field_value_to_model(doc_id: uuid.UUID, fv: DocumentFieldValue) -> DocumentFieldValueModel:
        return DocumentFieldValueModel(
            id=fv.id or uuid.uuid4(),
            document_id=doc_id,
            category_field_id=fv.category_field_id,
            value=fv.value,
        )

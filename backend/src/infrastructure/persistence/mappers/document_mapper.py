import uuid

from src.domain.document.entity import Document
from src.domain.document.value_objects import DocumentAttachment, DocumentFieldValue
from src.infrastructure.persistence.models import DocumentAttachmentModel, DocumentFieldValueModel, DocumentModel


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

        attachments = [
            DocumentAttachment(
                id=a.id,
                document_id=a.document_id,
                file_path=a.file_path,
                original_filename=a.original_filename,
                sort_order=a.sort_order,
                created_at=a.created_at,
            )
            for a in model.attachments
        ] if model.attachments else []

        return Document(
            id=model.id,
            year_id=model.year_id,
            category_id=model.category_id,
            title=model.title,
            document_number=model.document_number,
            date=model.date,
            short_desc=model.short_desc,
            pages=model.pages,
            file_path=model.file_path,
            signer=model.signer,
            archive_number=model.archive_number,
            year_value=model.year.value if model.year else model.year_id,
            person_id=model.person_id,
            person_name=model.person.full_name if model.person else None,
            person_position=DocumentMapper._get_person_position(model) if model.person else None,
            created_by=model.created_by,
            field_values=field_values,
            attachments=attachments,
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
            pages=entity.pages,
            file_path=entity.file_path,
            signer=entity.signer,
            archive_number=entity.archive_number,
            person_id=entity.person_id,
            created_by=entity.created_by,
        )
        return model

    @staticmethod
    def update_model(model: DocumentModel, entity: Document) -> None:
        model.category_id = entity.category_id
        model.title = entity.title
        model.document_number = entity.document_number
        model.date = entity.date
        model.short_desc = entity.short_desc
        model.pages = entity.pages
        model.file_path = entity.file_path
        model.signer = entity.signer
        model.archive_number = entity.archive_number
        model.person_id = entity.person_id

    @staticmethod
    def field_value_to_model(doc_id: uuid.UUID, fv: DocumentFieldValue) -> DocumentFieldValueModel:
        return DocumentFieldValueModel(
            id=fv.id or uuid.uuid4(),
            document_id=doc_id,
            category_field_id=fv.category_field_id,
            value=fv.value,
        )

    @staticmethod
    def _get_person_position(model: DocumentModel) -> str | None:
        if not model.person or not model.person.tenures:
            return None
        # Find tenure active on document date
        for t in model.person.tenures:
            if t.start_date <= model.date and (t.end_date is None or t.end_date >= model.date):
                end = t.end_date.strftime('%d.%m.%Y') if t.end_date else 'hozirgacha'
                return f"{t.position} ({t.start_date.strftime('%d.%m.%Y')} — {end})"
        # Fallback to most recent tenure
        t = model.person.tenures[0]
        end = t.end_date.strftime('%d.%m.%Y') if t.end_date else 'hozirgacha'
        return f"{t.position} ({t.start_date.strftime('%d.%m.%Y')} — {end})"

    @staticmethod
    def attachment_to_model(attachment: DocumentAttachment) -> DocumentAttachmentModel:
        return DocumentAttachmentModel(
            id=attachment.id,
            document_id=attachment.document_id,
            file_path=attachment.file_path,
            original_filename=attachment.original_filename,
            sort_order=attachment.sort_order,
        )

import datetime as dt
import uuid

from pydantic import BaseModel, Field, model_validator

from src.domain.document.value_objects import DocumentView

# Required extra fields per document view (Hujjat ko'rinishi).
# Locked in tasks/plan.md — internal/unknown require nothing beyond the common set.
REQUIRED_EXTRAS_BY_VIEW: dict[DocumentView, tuple[str, ...]] = {
    DocumentView.INCOMING: ("received_date", "origin_organization"),
    DocumentView.OUTGOING: ("sent_date", "recipient_organization"),
    # Murojaat (appeal): the reference form marks no field as strictly required,
    # so the rich appeal field set is all optional — see tasks/todo.md.
    DocumentView.APPEAL: (),
    DocumentView.INTERNAL: (),
    DocumentView.UNKNOWN: (),
}


def _missing_extras(view: DocumentView, values: "BaseModel") -> list[str]:
    missing = []
    for field_name in REQUIRED_EXTRAS_BY_VIEW.get(view, ()):
        if getattr(values, field_name, None) in (None, ""):
            missing.append(field_name)
    return missing


class CreateDocumentRequest(BaseModel):
    year_id: int
    category_id: uuid.UUID
    title: str = Field(min_length=1, max_length=500)
    document_number: str = Field(min_length=1, max_length=100)
    date: dt.date
    short_desc: str | None = None
    pages: int | None = Field(default=None, ge=0)
    signer: str | None = None
    archive_number: str | None = None
    person_id: uuid.UUID | None = None
    dynamic_fields: dict[str, str] = Field(default_factory=dict)
    # Phase 3 — document view + universal fields
    document_view: DocumentView = DocumentView.UNKNOWN
    archive_folder_id: uuid.UUID | None = None
    document_type_id: uuid.UUID | None = None
    document_form: str | None = Field(default=None, max_length=100)
    sender: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=20)
    related_document_number: str | None = Field(default=None, max_length=100)
    related_document_date: dt.date | None = None
    # Phase 3 — view-specific fields
    received_date: dt.date | None = None
    origin_organization: str | None = Field(default=None, max_length=255)
    sent_date: dt.date | None = None
    recipient_organization: str | None = Field(default=None, max_length=255)
    applicant_full_name: str | None = Field(default=None, max_length=255)
    applicant_phone: str | None = Field(default=None, max_length=50)
    # Murojaat (appeal) — reference FKs + extra fields
    region_id: uuid.UUID | None = None
    country_id: uuid.UUID | None = None
    reception_place_id: uuid.UUID | None = None
    appeal_type_id: uuid.UUID | None = None
    person_type: str | None = Field(default=None, max_length=50)
    outgoing_number: str | None = Field(default=None, max_length=100)
    outgoing_date: dt.date | None = None
    signed_by: str | None = Field(default=None, max_length=255)
    note: str | None = None

    @model_validator(mode="after")
    def _check_required_extras(self) -> "CreateDocumentRequest":
        missing = _missing_extras(self.document_view, self)
        if missing:
            raise ValueError(
                f"document_view '{self.document_view.value}' requires: {', '.join(missing)}"
            )
        return self


class UpdateDocumentRequest(BaseModel):
    category_id: uuid.UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=500)
    document_number: str | None = Field(default=None, min_length=1, max_length=100)
    date: dt.date | None = None
    short_desc: str | None = None
    pages: int | None = Field(default=None, ge=0)
    signer: str | None = None
    archive_number: str | None = None
    person_id: uuid.UUID | None = None
    dynamic_fields: dict[str, str] | None = None
    # Phase 3 — document view + universal fields
    document_view: DocumentView | None = None
    archive_folder_id: uuid.UUID | None = None
    document_type_id: uuid.UUID | None = None
    document_form: str | None = Field(default=None, max_length=100)
    sender: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=20)
    related_document_number: str | None = Field(default=None, max_length=100)
    related_document_date: dt.date | None = None
    # Phase 3 — view-specific fields
    received_date: dt.date | None = None
    origin_organization: str | None = Field(default=None, max_length=255)
    sent_date: dt.date | None = None
    recipient_organization: str | None = Field(default=None, max_length=255)
    applicant_full_name: str | None = Field(default=None, max_length=255)
    applicant_phone: str | None = Field(default=None, max_length=50)
    # Murojaat (appeal) — reference FKs + extra fields
    region_id: uuid.UUID | None = None
    country_id: uuid.UUID | None = None
    reception_place_id: uuid.UUID | None = None
    appeal_type_id: uuid.UUID | None = None
    person_type: str | None = Field(default=None, max_length=50)
    outgoing_number: str | None = Field(default=None, max_length=100)
    outgoing_date: dt.date | None = None
    signed_by: str | None = Field(default=None, max_length=255)
    note: str | None = None

    @model_validator(mode="after")
    def _check_required_extras(self) -> "UpdateDocumentRequest":
        # Only enforce when the caller is explicitly (re)setting the view —
        # a partial update that doesn't touch document_view skips this check.
        if self.document_view is not None:
            missing = _missing_extras(self.document_view, self)
            if missing:
                raise ValueError(
                    f"document_view '{self.document_view.value}' requires: {', '.join(missing)}"
                )
        return self


class AttachmentResponse(BaseModel):
    id: uuid.UUID
    file_path: str
    original_filename: str
    sort_order: int
    created_at: dt.datetime


class DocumentFieldValueResponse(BaseModel):
    category_field_id: uuid.UUID
    value: str | None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    year_id: int
    category_id: uuid.UUID
    title: str
    document_number: str
    date: dt.date
    short_desc: str | None
    pages: int | None
    file_path: str | None
    signer: str | None
    archive_number: str | None
    person_id: uuid.UUID | None
    person_name: str | None
    person_position: str | None
    created_by: uuid.UUID | None
    # Phase 3 — document view + universal fields
    document_view: DocumentView
    archive_folder_id: uuid.UUID | None
    document_type_id: uuid.UUID | None
    document_type_name: str | None
    document_form: str | None
    sender: str | None
    language: str | None
    related_document_number: str | None
    related_document_date: dt.date | None
    # Phase 3 — view-specific fields
    received_date: dt.date | None
    origin_organization: str | None
    sent_date: dt.date | None
    recipient_organization: str | None
    applicant_full_name: str | None
    applicant_phone: str | None
    # Murojaat (appeal) — reference FKs + extra fields
    region_id: uuid.UUID | None
    country_id: uuid.UUID | None
    reception_place_id: uuid.UUID | None
    appeal_type_id: uuid.UUID | None
    person_type: str | None
    outgoing_number: str | None
    outgoing_date: dt.date | None
    signed_by: str | None
    note: str | None
    field_values: list[DocumentFieldValueResponse]
    attachments: list[AttachmentResponse] = Field(default_factory=list)
    created_at: dt.datetime
    updated_at: dt.datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int

import json
import uuid
from datetime import date as date_type, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, String, Text, TypeDecorator, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import CHAR, JSON


class GUID(TypeDecorator):
    """Platform-independent UUID. Native ``UUID`` on PostgreSQL; ``CHAR(36)`` elsewhere."""

    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class JSONType(TypeDecorator):
    """Platform-independent JSON. ``JSONB`` on PostgreSQL; ``JSON`` elsewhere."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB())
        return dialect.type_descriptor(JSON())


class Base(DeclarativeBase):
    pass


class MusicSchoolModel(Base):
    __tablename__ = "music_schools"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)



class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    music_school_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("music_schools.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    department: Mapped["DepartmentModel | None"] = relationship()
    music_school: Mapped["MusicSchoolModel | None"] = relationship()



class CategoryModel(Base):
    """Nomenklatura — top-level document grouping (the Year concept was removed)."""

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    fields: Mapped[list["CategoryFieldModel"]] = relationship(back_populates="category", cascade="all, delete-orphan", order_by="CategoryFieldModel.sort_order")

    # A nomenklatura is a unique year number (e.g. "2024") — no duplicates.
    __table_args__ = (UniqueConstraint("name", name="uq_categories_name"),)


class CategoryFieldModel(Base):
    __tablename__ = "category_fields"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    options: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    placeholder: Mapped[str | None] = mapped_column(String(255), nullable=True)
    validation: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    category: Mapped["CategoryModel"] = relationship(back_populates="fields")

    __table_args__ = (UniqueConstraint("category_id", "name"),)


class DefaultFieldModel(Base):
    __tablename__ = "default_fields"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    options: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    placeholder: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class DepartmentModel(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    index_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)


class ArchiveFolderModel(Base):
    __tablename__ = "archive_folders"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    index_code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    article_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # "Ro'yxat raqami" — registry/list number, surfaced after "Modda raqami".
    list_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    retention_period_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("retention_periods.id", ondelete="SET NULL"), nullable=True
    )
    # "Umumiy varaqlar soni" — manually-entered total sheet count. The automatic
    # sum of the folder's documents' pages is computed at query time, not stored.
    total_sheets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # start_date / end_date are re-surfaced by the redesigned form.
    start_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    retention_period: Mapped["RetentionPeriodModel | None"] = relationship()
    department: Mapped["DepartmentModel | None"] = relationship()


class DocumentTypeModel(Base):
    __tablename__ = "document_types"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)


class RegionModel(Base):
    """Hudud — region/country reference. type='LOCAL' (viloyat) or 'ABROAD' (xorijiy davlat)."""

    __tablename__ = "regions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class ReceptionPlaceModel(Base):
    """Qabul qilingan joy — where an appeal was received."""

    __tablename__ = "reception_places"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class AppealTypeModel(Base):
    """Murojaat turi — kind of appeal (Ariza, Taklif, Shikoyat, So'rov)."""

    __tablename__ = "appeal_types"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class RetentionPeriodModel(Base):
    """Saqlash muddati — archival retention period reference (3 yil, Doimiy, …)."""

    __tablename__ = "retention_periods"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class PersonModel(Base):
    __tablename__ = "persons"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    tenures: Mapped[list["PersonTenureModel"]] = relationship(back_populates="person", cascade="all, delete-orphan", order_by="PersonTenureModel.start_date.desc()")


class PersonTenureModel(Base):
    __tablename__ = "person_tenures"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    person_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    end_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    person: Mapped["PersonModel"] = relationship(back_populates="tenures")


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    short_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    signer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    archive_number: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    person_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("persons.id"), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    # Phase 3 — document view + universal fields
    document_view: Mapped[str] = mapped_column(String(20), nullable=False, server_default="unknown")
    archive_folder_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("archive_folders.id", ondelete="SET NULL"), nullable=True
    )
    document_form: Mapped[str | None] = mapped_column(String(100), nullable=True)
    document_type_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("document_types.id", ondelete="SET NULL"), nullable=True
    )
    sender: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    related_document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    related_document_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    # Phase 3 — view-specific fields
    received_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    origin_organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    recipient_organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    applicant_full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    applicant_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Murojaat (appeal) — view-specific fields matching the reference form
    region_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("regions.id", ondelete="SET NULL"), nullable=True
    )
    country_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("regions.id", ondelete="SET NULL"), nullable=True
    )
    reception_place_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("reception_places.id", ondelete="SET NULL"), nullable=True
    )
    appeal_type_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("appeal_types.id", ondelete="SET NULL"), nullable=True
    )
    person_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    outgoing_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    outgoing_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    signed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Phase 6 — OCR pipeline. extracted_text is the source of truth (PG)
    # so we can reindex into ES without re-OCR. ocr_status tracks lifecycle:
    # pending → processing → done | failed | skipped.
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    ocr_completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped["CategoryModel"] = relationship()
    person: Mapped["PersonModel | None"] = relationship()
    archive_folder: Mapped["ArchiveFolderModel | None"] = relationship()
    document_type: Mapped["DocumentTypeModel | None"] = relationship()
    region: Mapped["RegionModel | None"] = relationship(foreign_keys=[region_id])
    country: Mapped["RegionModel | None"] = relationship(foreign_keys=[country_id])
    reception_place: Mapped["ReceptionPlaceModel | None"] = relationship()
    appeal_type: Mapped["AppealTypeModel | None"] = relationship()
    field_values: Mapped[list["DocumentFieldValueModel"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    attachments: Mapped[list["DocumentAttachmentModel"]] = relationship(back_populates="document", cascade="all, delete-orphan", order_by="DocumentAttachmentModel.sort_order")


class DocumentFieldValueModel(Base):
    __tablename__ = "document_field_values"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    category_field_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("category_fields.id", ondelete="CASCADE"), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped["DocumentModel"] = relationship(back_populates="field_values")
    category_field: Mapped["CategoryFieldModel"] = relationship()

    __table_args__ = (UniqueConstraint("document_id", "category_field_id"),)


class DocumentAttachmentModel(Base):
    __tablename__ = "document_attachments"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Phase 6 — same OCR lifecycle as DocumentModel.
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    ocr_completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    document: Mapped["DocumentModel"] = relationship(back_populates="attachments")


class SearchIndexJobModel(Base):
    """Outbox: each row is a pending index/delete operation for the search worker.

    Written in the same DB transaction as the document save/delete so durability
    of the index job piggybacks on the durability of the data change. No FK to
    ``documents`` — a row carrying ``op='delete'`` deliberately outlives the
    deleted document, and an ``op='index'`` row for a now-deleted document is
    handled at drain time (it converts to a delete).
    """

    __tablename__ = "search_index_jobs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False)
    op: Mapped[str] = mapped_column(String(10), nullable=False)  # "index" | "delete"
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True, server_default="general")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    __table_args__ = (Index("ix_search_index_jobs_created_at", "created_at"),)


class MusicSchoolSpecialtyModel(Base):
    __tablename__ = "music_school_specialties"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    music_school_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("music_schools.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    music_school: Mapped["MusicSchoolModel"] = relationship()

    __table_args__ = (
        UniqueConstraint("music_school_id", "name", name="uq_music_school_specialty_name"),
    )


class MusicSchoolDocumentModel(Base):
    __tablename__ = "music_school_documents"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    student_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    music_school_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("music_schools.id", ondelete="RESTRICT"), nullable=False
    )
    specialty_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("music_school_specialties.id", ondelete="RESTRICT"), nullable=False
    )
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=False)
    diploma_serial: Mapped[str] = mapped_column(String(50), nullable=False)
    diploma_number: Mapped[str] = mapped_column(String(50), nullable=False)
    given_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    
    passport_series: Mapped[str | None] = mapped_column(String(10), nullable=True)
    passport_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pinfl: Mapped[str | None] = mapped_column(String(14), nullable=True)

    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    ocr_completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    music_school: Mapped["MusicSchoolModel"] = relationship()
    specialty: Mapped["MusicSchoolSpecialtyModel"] = relationship()


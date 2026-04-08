import uuid
from datetime import date as date_type, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)


class YearModel(Base):
    __tablename__ = "years"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    value: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    year_categories: Mapped[list["YearCategoryModel"]] = relationship(back_populates="year", cascade="all, delete-orphan")


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    fields: Mapped[list["CategoryFieldModel"]] = relationship(back_populates="category", cascade="all, delete-orphan", order_by="CategoryFieldModel.sort_order")
    year_categories: Mapped[list["YearCategoryModel"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class YearCategoryModel(Base):
    __tablename__ = "year_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year_id: Mapped[int] = mapped_column(Integer, ForeignKey("years.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    year: Mapped["YearModel"] = relationship(back_populates="year_categories")
    category: Mapped["CategoryModel"] = relationship(back_populates="year_categories")

    __table_args__ = (UniqueConstraint("year_id", "category_id"),)


class CategoryFieldModel(Base):
    __tablename__ = "category_fields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    placeholder: Mapped[str | None] = mapped_column(String(255), nullable=True)
    validation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    category: Mapped["CategoryModel"] = relationship(back_populates="fields")

    __table_args__ = (UniqueConstraint("category_id", "name"),)


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year_id: Mapped[int] = mapped_column(Integer, ForeignKey("years.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    short_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    target: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    signer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    year: Mapped["YearModel"] = relationship()
    category: Mapped["CategoryModel"] = relationship()
    field_values: Mapped[list["DocumentFieldValueModel"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentFieldValueModel(Base):
    __tablename__ = "document_field_values"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    category_field_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("category_fields.id", ondelete="CASCADE"), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped["DocumentModel"] = relationship(back_populates="field_values")
    category_field: Mapped["CategoryFieldModel"] = relationship()

    __table_args__ = (UniqueConstraint("document_id", "category_field_id"),)

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories.user_repository import SqlAlchemyUserRepository
from src.infrastructure.persistence.repositories.year_repository import SqlAlchemyYearRepository
from src.infrastructure.persistence.repositories.category_repository import SqlAlchemyCategoryRepository
from src.infrastructure.persistence.repositories.document_repository import SqlAlchemyDocumentRepository
from src.infrastructure.persistence.repositories.person_repository import SqlAlchemyPersonRepository
from src.infrastructure.persistence.repositories.department_repository import SqlAlchemyDepartmentRepository
from src.infrastructure.persistence.repositories.archive_folder_repository import SqlAlchemyArchiveFolderRepository
from src.infrastructure.persistence.repositories.document_type_repository import SqlAlchemyDocumentTypeRepository
from src.infrastructure.file_storage.local_storage import FileStorageService
from src.application.user.handlers import UserCommandHandler, UserQueryHandler
from src.application.year.handlers import YearCommandHandler, YearQueryHandler
from src.application.category.handlers import CategoryCommandHandler, CategoryQueryHandler
from src.application.document.handlers import DocumentCommandHandler, DocumentQueryHandler
from src.application.person.handlers import PersonCommandHandler, PersonQueryHandler
from src.application.department.handlers import DepartmentCommandHandler, DepartmentQueryHandler
from src.application.archive_folder.handlers import ArchiveFolderCommandHandler, ArchiveFolderQueryHandler
from src.application.document_type.handlers import DocumentTypeCommandHandler, DocumentTypeQueryHandler


# User
def get_user_command_handler(session: AsyncSession = Depends(get_session)) -> UserCommandHandler:
    return UserCommandHandler(SqlAlchemyUserRepository(session))


def get_user_query_handler(session: AsyncSession = Depends(get_session)) -> UserQueryHandler:
    return UserQueryHandler(SqlAlchemyUserRepository(session))


# Year
def get_year_command_handler(session: AsyncSession = Depends(get_session)) -> YearCommandHandler:
    return YearCommandHandler(SqlAlchemyYearRepository(session))


def get_year_query_handler(session: AsyncSession = Depends(get_session)) -> YearQueryHandler:
    return YearQueryHandler(SqlAlchemyYearRepository(session))


# Category
def get_category_command_handler(session: AsyncSession = Depends(get_session)) -> CategoryCommandHandler:
    return CategoryCommandHandler(SqlAlchemyCategoryRepository(session))


def get_category_query_handler(session: AsyncSession = Depends(get_session)) -> CategoryQueryHandler:
    return CategoryQueryHandler(SqlAlchemyCategoryRepository(session))


# Document
def get_document_command_handler(session: AsyncSession = Depends(get_session)) -> DocumentCommandHandler:
    return DocumentCommandHandler(
        document_repo=SqlAlchemyDocumentRepository(session),
        category_repo=SqlAlchemyCategoryRepository(session),
        year_repo=SqlAlchemyYearRepository(session),
        file_storage=FileStorageService(),
    )


def get_document_query_handler(session: AsyncSession = Depends(get_session)) -> DocumentQueryHandler:
    return DocumentQueryHandler(SqlAlchemyDocumentRepository(session))


# Person
def get_person_command_handler(session: AsyncSession = Depends(get_session)) -> PersonCommandHandler:
    return PersonCommandHandler(SqlAlchemyPersonRepository(session))


def get_person_query_handler(session: AsyncSession = Depends(get_session)) -> PersonQueryHandler:
    return PersonQueryHandler(SqlAlchemyPersonRepository(session))


# Department
def get_department_command_handler(session: AsyncSession = Depends(get_session)) -> DepartmentCommandHandler:
    return DepartmentCommandHandler(SqlAlchemyDepartmentRepository(session))


def get_department_query_handler(session: AsyncSession = Depends(get_session)) -> DepartmentQueryHandler:
    return DepartmentQueryHandler(SqlAlchemyDepartmentRepository(session))


# Archive Folder
def get_archive_folder_command_handler(session: AsyncSession = Depends(get_session)) -> ArchiveFolderCommandHandler:
    return ArchiveFolderCommandHandler(SqlAlchemyArchiveFolderRepository(session))


def get_archive_folder_query_handler(session: AsyncSession = Depends(get_session)) -> ArchiveFolderQueryHandler:
    return ArchiveFolderQueryHandler(SqlAlchemyArchiveFolderRepository(session))


# Document Type
def get_document_type_command_handler(session: AsyncSession = Depends(get_session)) -> DocumentTypeCommandHandler:
    return DocumentTypeCommandHandler(SqlAlchemyDocumentTypeRepository(session))


def get_document_type_query_handler(session: AsyncSession = Depends(get_session)) -> DocumentTypeQueryHandler:
    return DocumentTypeQueryHandler(SqlAlchemyDocumentTypeRepository(session))

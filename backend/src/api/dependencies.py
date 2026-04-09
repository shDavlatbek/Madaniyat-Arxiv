from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories.user_repository import SqlAlchemyUserRepository
from src.infrastructure.persistence.repositories.year_repository import SqlAlchemyYearRepository
from src.infrastructure.persistence.repositories.category_repository import SqlAlchemyCategoryRepository
from src.infrastructure.persistence.repositories.document_repository import SqlAlchemyDocumentRepository
from src.infrastructure.persistence.repositories.person_repository import SqlAlchemyPersonRepository
from src.infrastructure.file_storage.local_storage import FileStorageService
from src.application.user.handlers import UserCommandHandler, UserQueryHandler
from src.application.year.handlers import YearCommandHandler, YearQueryHandler
from src.application.category.handlers import CategoryCommandHandler, CategoryQueryHandler
from src.application.document.handlers import DocumentCommandHandler, DocumentQueryHandler
from src.application.person.handlers import PersonCommandHandler, PersonQueryHandler


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

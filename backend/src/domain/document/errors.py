from src.domain.shared.errors import DomainError, NotFoundError


class DocumentNotFoundError(NotFoundError):
    def __init__(self, document_id: str | None = None):
        super().__init__("Document", document_id)


class InvalidFieldValueError(DomainError):
    def __init__(self, field_name: str, reason: str):
        super().__init__(f"Invalid value for field '{field_name}': {reason}")

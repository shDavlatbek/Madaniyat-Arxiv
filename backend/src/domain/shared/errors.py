class DomainError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, entity_name: str, identifier: str | None = None):
        msg = f"{entity_name} not found"
        if identifier:
            msg = f"{entity_name} with id '{identifier}' not found"
        super().__init__(msg)


class ValidationError(DomainError):
    pass


class AuthorizationError(DomainError):
    pass

from fastapi import HTTPException, status


class CustomException(Exception):
    """Base custom exception"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type: str = "INTERNAL_ERROR",
        detail: str = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.detail = detail
        super().__init__(self.message)


class ValidationException(CustomException):
    """Validation exception"""
    def __init__(self, message: str, detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="VALIDATION_ERROR",
            detail=detail
        )


class NotFoundException(CustomException):
    """Not found exception"""
    def __init__(self, message: str = "Resource not found", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="NOT_FOUND",
            detail=detail
        )


class AuthenticationException(CustomException):
    """Authentication exception"""
    def __init__(self, message: str = "Authentication failed", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="AUTHENTICATION_ERROR",
            detail=detail
        )


class AuthorizationException(CustomException):
    """Authorization exception"""
    def __init__(self, message: str = "Not enough permissions", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="AUTHORIZATION_ERROR",
            detail=detail
        )


class ConflictException(CustomException):
    """Conflict exception"""
    def __init__(self, message: str = "Resource already exists", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_type="CONFLICT_ERROR",
            detail=detail
        )

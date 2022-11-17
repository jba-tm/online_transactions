from fastapi import status, HTTPException, Request
from typing import Any, Optional, Dict
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.utils.translation import gettext as _


async def validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": _(str(exc))},
    )


class ImproperlyConfigured(Exception):
    """Somehow improperly configured"""
    pass


class InvalidToken(HTTPException):
    def __init__(
            self,
            status_code: int = status.HTTP_401_UNAUTHORIZED,
            detail: Any = 'Invalid token',
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnAuthenticated(HTTPException):
    def __init__(
            self,
            status_code: int = status.HTTP_401_UNAUTHORIZED,
            detail: Any = 'Un authenticated',
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class PermissionDenied(HTTPException):
    def __init__(
            self,
            status_code: Optional[int] = status.HTTP_403_FORBIDDEN,
            detail: Optional[str] = _('Permission denied'),
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class DoesNotExist(HTTPException):
    def __init__(
            self,
            detail: Optional[str] = None,
            *args, **kwargs
    ) -> None:
        if detail is None:
            detail = _('Requested page does not exist')
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND, *args, **kwargs)

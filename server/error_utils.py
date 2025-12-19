"""
Helpers for converting arbitrary exceptions into the AppError hierarchy.
"""

from __future__ import annotations

from typing import Iterable, Tuple, Type

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from server.errors import (
    AppError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)


HTTP_STATUS_TO_ERROR: Iterable[Tuple[Tuple[int, ...], Type[AppError]]] = (
    ((400, 422), BadRequestError),
    ((401,), UnauthorizedError),
    ((403,), ForbiddenError),
    ((404,), NotFoundError),
    ((409,), ConflictError),
)


def map_exception(exc: Exception) -> AppError:
    """
    Map any exception to an AppError instance.

    Handles:
    - AppError instances (returns as-is)
    - FastAPI HTTPException
    - Standard Python exceptions (ValueError, FileNotFoundError, KeyError)
    """
    if isinstance(exc, AppError):
        return exc

    if isinstance(exc, HTTPException):
        return _map_http_exception(exc)

    # Map standard Python exceptions
    if isinstance(exc, ValueError):
        return BadRequestError(str(exc))

    if isinstance(exc, FileNotFoundError):
        return NotFoundError(str(exc))

    if isinstance(exc, KeyError):
        return BadRequestError(f"Missing key: {str(exc)}", extra={"error_type": "key_error"})

    return AppError(str(exc))


def _map_http_exception(exc: HTTPException) -> AppError:
    for status_codes, error_cls in HTTP_STATUS_TO_ERROR:
        if exc.status_code in status_codes:
            return error_cls(str(exc.detail) if exc.detail else None)
    return AppError(
        str(exc.detail) if exc.detail else None,
        status_code=exc.status_code,
    )


async def unified_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    app_error = map_exception(exc)
    return JSONResponse(
        status_code=app_error.status_code,
        content=app_error.to_dict(),
    )

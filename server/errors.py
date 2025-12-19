"""
Unified application error hierarchy for the FastAPI server.
"""

import traceback
from typing import Any, Dict, Optional


class AppError(Exception):
    """
    Base class for all application-level errors.

    Provides a consistent payload structure so the API always responds with
    predictable JSON.
    """
    code = "app_error"
    status_code = 500

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.message = message or self.__class__.__name__
        self.extra = extra or {}
        self.trace = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"error": self.code, "message": self.message}
        if self.extra:
            payload["details"] = self.extra
        return payload


class BadRequestError(AppError):
    code = "bad_request"
    status_code = 400


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404


class UnauthorizedError(AppError):
    code = "unauthorized"
    status_code = 401


class ForbiddenError(AppError):
    code = "forbidden"
    status_code = 403


class ConflictError(AppError):
    code = "conflict"
    status_code = 409

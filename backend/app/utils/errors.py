from fastapi import HTTPException


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BadRequestError(AppError):
    status_code = 400
    code = "bad_request"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


def as_http_500(prefix: str, exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=f"{prefix}: {str(exc)}")

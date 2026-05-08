"""Common response schemas."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class ErrorDetail(BaseModel):
    """Structured error detail."""

    code: str
    message: str
    detail: str | None = None
    correlation_id: str | None = None


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: ErrorDetail


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total: int
    total_pages: int

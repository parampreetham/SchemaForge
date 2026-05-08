"""Global exception handler middleware."""

from datetime import UTC, datetime

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions and return structured JSON error responses."""
    correlation_id = request.headers.get("X-Correlation-ID", "unknown")

    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "detail": str(exc) if True else None,  # Only in debug mode
                "correlation_id": correlation_id,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        },
    )

"""Health check endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Liveness check — returns OK if the API process is running."""
    return {
        "status": "ok",
        "service": "schemaforge-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check — verifies database and Redis connectivity."""
    checks = {}

    # Check PostgreSQL
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "detail": str(e)}

    # Check Redis
    try:
        from app.core.redis import redis_client

        redis_client.ping()
        checks["redis"] = {"status": "ok"}
    except Exception as e:
        checks["redis"] = {"status": "error", "detail": str(e)}

    # Overall status
    all_ok = all(c["status"] == "ok" for c in checks.values())

    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.now(UTC).isoformat(),
    }

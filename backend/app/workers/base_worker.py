"""Base worker functionality and task context management."""

import uuid
from typing import Callable, Any
from functools import wraps

import structlog
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.pipeline_job import PipelineJob

logger = structlog.get_logger()

def job_context(func: Callable) -> Callable:
    """Decorator to manage database session and logging context for background jobs."""
    @wraps(func)
    def wrapper(job_id: uuid.UUID, *args, **kwargs) -> Any:
        db: Session = SessionLocal()
        # Bind correlation ID for logging
        log = logger.bind(job_id=str(job_id), worker_function=func.__name__)
        
        try:
            log.info("Job started")
            # Fetch the job if applicable (most of our tasks revolve around a PipelineJob or ChunkTask)
            # In base context, we just pass the DB session
            result = func(db, job_id, *args, **kwargs)
            db.commit()
            log.info("Job completed successfully")
            return result
        except Exception as e:
            db.rollback()
            log.exception("Job failed", error=str(e))
            # Re-raise so RQ handles the failure properly
            raise
        finally:
            db.close()
            
    return wrapper

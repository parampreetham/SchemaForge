"""Validation Worker."""

import uuid
import time
import structlog
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.models.pipeline_job import PipelineJob
from app.models.chunk_task import ChunkTask
from app.models.validation_result import ValidationResult
from app.services.validation.validator import Validator
from app.workers.base_worker import job_context

logger = structlog.get_logger()

MAX_RETRIES = 3

@job_context
def validate_chunk_job(db: Session, job_id: uuid.UUID, chunk_task_id: str):
    """Worker function to validate converted SQL against target database."""
    task = db.query(ChunkTask).filter(ChunkTask.id == chunk_task_id).first()
    if not task:
        logger.error("ChunkTask not found", chunk_task_id=chunk_task_id)
        return

    job = db.query(PipelineJob).filter(PipelineJob.id == str(job_id)).first()
    if job and job.cancel_requested:
        task.status = "cancelled"
        db.commit()
        return

    # We only validate chunks that have been converted or translated
    if not task.converted_sql:
        logger.warning("Chunk has no converted_sql to validate", chunk_task_id=chunk_task_id)
        return

    task.status = "validating"
    db.commit()

    start_time = time.time()
    
    try:
        logger.info("Validating chunk", chunk_task_id=chunk_task_id, object_type=task.object_type)
        
        passed, error_details = Validator.full_validation(task.converted_sql)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Determine attempt number
        attempt_number = db.query(ValidationResult).filter(ValidationResult.task_id == task.id).count() + 1
        
        # Create validation result record
        val_result = ValidationResult(
            task_id=task.id,
            attempt_number=attempt_number,
            passed=passed,
            error_code=error_details.get("error_code"),
            error_message=error_details.get("error_message"),
            error_line=error_details.get("error_line"),
            validated_sql=task.converted_sql,
            execution_time_ms=latency_ms
        )
        db.add(val_result)
        
        if passed:
            task.status = "validated"
            task.completed_at = datetime.now(UTC)
            logger.info("Validation passed", chunk_task_id=chunk_task_id)
        else:
            task.retry_count = (task.retry_count or 0) + 1
            if task.retry_count <= MAX_RETRIES:
                task.status = "needs_ai"  # Route to AI queue for correction
                logger.info("Validation failed, sending to AI for retry", chunk_task_id=chunk_task_id, retries=task.retry_count)
            else:
                task.status = "failed_validation" # Exhausted retries, manual review needed
                task.error_message = f"Validation failed after {MAX_RETRIES} retries: {error_details.get('error_message')}"
                task.completed_at = datetime.now(UTC)
                logger.error("Validation failed, max retries reached", chunk_task_id=chunk_task_id)
                
                if job:
                    job.failed_chunks += 1
        
        db.commit()
            
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        task.completed_at = datetime.now(UTC)
        db.commit()
        
        if job:
            job.failed_chunks += 1
            db.commit()
            
        logger.exception("Validation worker crashed", chunk_task_id=chunk_task_id, error=str(e))
        raise

"""Conversion worker responsible for running deterministic rules."""

import uuid
import structlog
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.models.pipeline_job import PipelineJob
from app.models.chunk_task import ChunkTask
from app.services.conversion.engine import ConversionEngine
from app.workers.base_worker import job_context

logger = structlog.get_logger()

@job_context
def convert_chunk_job(db: Session, job_id: uuid.UUID, chunk_task_id: str):
    """Worker function to convert a single chunk."""
    # 1. Fetch Task
    task = db.query(ChunkTask).filter(ChunkTask.id == chunk_task_id).first()
    if not task:
        logger.error("ChunkTask not found", chunk_task_id=chunk_task_id)
        return

    # Fetch Job
    job = db.query(PipelineJob).filter(PipelineJob.id == str(job_id)).first()
    if job and job.cancel_requested:
        task.status = "cancelled"
        db.commit()
        return

    task.status = "converting"
    task.started_at = datetime.now(UTC)
    db.commit()

    try:
        # 2. Run Engine
        logger.info("Converting chunk", chunk_task_id=chunk_task_id, object_type=task.object_type)
        metadata = {
            "object_type": task.object_type,
            "object_name": task.object_name
        }
        
        converted_sql, new_status, error_msg = ConversionEngine.convert(task.original_sql, metadata)
        
        # 3. Update Task
        task.converted_sql = converted_sql
        task.status = new_status
        task.error_message = error_msg
        task.conversion_method = "deterministic" if new_status == "converted" else None
        task.completed_at = datetime.now(UTC)
        
        db.commit()
        
        if new_status == "converted":
            # Update job progress safely
            # Note: For production with concurrent workers, use atomic updates
            if job:
                job.completed_chunks += 1
                job.progress_pct = (job.completed_chunks / max(1, job.total_chunks)) * 100
                db.commit()
            
            # Enqueue to Validation Worker (Phase 5)
            # queue.enqueue("validation", task.id)
            pass
        elif new_status == "needs_ai":
            # Enqueue to AI Worker (Phase 4)
            # queue.enqueue("ai_translation", task.id)
            pass
        
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        task.completed_at = datetime.now(UTC)
        db.commit()
        
        if job:
            job.failed_chunks += 1
            db.commit()
            
        logger.exception("Conversion failed", chunk_task_id=chunk_task_id, error=str(e))
        raise

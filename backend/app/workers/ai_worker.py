"""AI translation worker."""

import uuid
import time
import structlog
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from app.models.pipeline_job import PipelineJob
from app.models.chunk_task import ChunkTask
from app.models.ai_interaction import AIInteraction
from app.services.ai.engine import AIEngine
from app.workers.base_worker import job_context

logger = structlog.get_logger()

@job_context
def translate_chunk_job(db: Session, job_id: uuid.UUID, chunk_task_id: str):
    """Worker function to translate a chunk using AI."""
    task = db.query(ChunkTask).filter(ChunkTask.id == chunk_task_id).first()
    if not task:
        logger.error("ChunkTask not found", chunk_task_id=chunk_task_id)
        return

    job = db.query(PipelineJob).filter(PipelineJob.id == str(job_id)).first()
    if job and job.cancel_requested:
        task.status = "cancelled"
        db.commit()
        return

    task.status = "translating"
    if not task.started_at:
        task.started_at = datetime.now(UTC)
    db.commit()

    start_time = time.time()
    
    try:
        logger.info("AI Translating chunk", chunk_task_id=chunk_task_id, object_type=task.object_type)
        
        converted_sql, metrics = AIEngine.translate(task.original_sql, task.object_type)
        
        latency_ms = int((time.time() - start_time) * 1000)
        metrics["latency_ms"] = latency_ms
        
        # Determine attempt number
        attempt_number = db.query(AIInteraction).filter(AIInteraction.task_id == task.id).count() + 1
        
        # Create interaction record
        interaction = AIInteraction(
            task_id=task.id,
            attempt_number=attempt_number,
            model=metrics["model"],
            prompt_version=metrics["prompt_version"],
            system_prompt=metrics["system_prompt"],
            user_prompt=metrics["user_prompt"],
            response=metrics["response"],
            input_tokens=metrics["input_tokens"],
            output_tokens=metrics["output_tokens"],
            cost_usd=metrics["cost_usd"],
            latency_ms=metrics["latency_ms"]
        )
        db.add(interaction)
        
        # Update Task
        task.converted_sql = converted_sql
        task.status = "translated"
        task.conversion_method = f"ai ({metrics['model']})"
        task.confidence_score = metrics["confidence_score"]
        task.completed_at = datetime.now(UTC)
        
        db.commit()
        
        if job:
            job.completed_chunks += 1
            job.progress_pct = (job.completed_chunks / max(1, job.total_chunks)) * 100
            db.commit()
            
        # Optional: enqueue to Validation Worker (Phase 5)
            
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        task.completed_at = datetime.now(UTC)
        db.commit()
        
        if job:
            job.failed_chunks += 1
            db.commit()
            
        logger.exception("AI Translation failed", chunk_task_id=chunk_task_id, error=str(e))
        raise

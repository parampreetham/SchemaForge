"""Parsing worker responsible for chunking DDL and determining dependencies."""

import uuid
import structlog
from sqlalchemy.orm import Session

from app.models.pipeline_job import PipelineJob
from app.models.chunk_task import ChunkTask
from app.services.parser import DDLChunker, DependencyGraph
from app.workers.base_worker import job_context

logger = structlog.get_logger()

@job_context
def parse_ddl_job(db: Session, job_id: uuid.UUID):
    """Worker function to parse a DDL file and create ordered ChunkTasks."""
    # 1. Fetch Job
    job = db.query(PipelineJob).filter(PipelineJob.id == str(job_id)).first()
    if not job:
        logger.error("PipelineJob not found", job_id=str(job_id))
        return

    if job.cancel_requested:
        job.status = "cancelled"
        return

    job.status = "parsing"
    db.commit()

    try:
        # 2. Read File (In MVP, we assume local file path accessible by worker)
        file_path = job.original_file_path
        if not file_path:
            raise ValueError("No original_file_path specified for PipelineJob")
        
        with open(file_path, "r", encoding="utf-8") as f:
            sql_text = f.read()

        # 3. Chunk DDL
        logger.info("Chunking DDL", file_path=file_path)
        chunks = DDLChunker.chunk_ddl(sql_text)
        
        # 4. Analyze Dependencies
        logger.info("Analyzing dependencies")
        graph = DependencyGraph()
        
        for i, chunk_sql in enumerate(chunks):
            # use a temporary chunk ID for the graph
            temp_chunk_id = f"temp_{i}"
            graph.add_chunk(temp_chunk_id, chunk_sql)
            
        ordered_chunks = graph.get_ordered_chunks()
        
        # 5. Create ChunkTasks in database
        logger.info("Creating ChunkTasks in DB", total=len(ordered_chunks))
        task_objects = []
        for chunk_info in ordered_chunks:
            # We don't link dependencies directly in MVP DB schema if we rely on dependency_order
            # to fetch tasks iteratively, or we can just rely on the queueing system.
            # In Phase 3, the conversion engine will fetch ordered chunks.
            task = ChunkTask(
                job_id=job.id,
                object_name=chunk_info["object_name"] or "Unknown",
                object_type=chunk_info["metadata"]["object_type"] or "UNKNOWN",
                original_sql=chunk_info["metadata"].get("sql", ""), # from graph data if we passed it, wait we didn't return sql in get_ordered_chunks
                status="pending",
                dependency_order=chunk_info["dependency_order"]
            )
            # Fetch the actual SQL
            # graph._chunks holds the SQL
            chunk_id = chunk_info["chunk_id"]
            task.original_sql = graph._chunks[chunk_id]["sql"]
            
            task_objects.append(task)
            
        db.add_all(task_objects)
        
        # 6. Update Job Status
        job.total_chunks = len(task_objects)
        job.status = "parsed"
        # We would enqueue conversion here if it was Phase 3
        # e.g., queue.enqueue(start_conversion_job, job.id)
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        logger.exception("Parsing failed", job_id=str(job_id), error=str(e))
        raise

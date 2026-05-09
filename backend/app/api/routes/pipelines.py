from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import os
import aiofiles

from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.pipeline_job import PipelineJob
from app.models.user import User
from app.core import settings
from rq import Queue
from redis import Redis

router = APIRouter(tags=["Pipelines"])

@router.post("/pipelines/upload")
async def upload_pipeline_schema(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a DB2 schema file and create a new PipelineJob."""
    if not file.filename.endswith(('.sql', '.ddl')):
        raise HTTPException(status_code=400, detail="Only .sql or .ddl files are supported.")
        
    # Ensure artifacts directory exists
    os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
    
    # Save the file
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(settings.ARTIFACTS_DIR, safe_filename)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    # Create DB Record
    new_job = PipelineJob(
        project_id=uuid.UUID("00000000-0000-0000-0000-000000000000"), # Default project for MVP
        created_by_id=current_user.id,
        status="PENDING",
        source_file_path=file_path,
        total_chunks=0,
        completed_chunks=0
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    return {"id": new_job.id, "status": "PENDING", "message": "File uploaded successfully."}

@router.post("/pipelines/{pipeline_id}/start")
async def start_pipeline(
    pipeline_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queue the parsing job to start the pipeline."""
    job = await db.get(PipelineJob, pipeline_id)
    if not job:
        raise HTTPException(status_code=404, detail="Pipeline not found")
        
    job.status = "RUNNING"
    await db.commit()
    
    # Enqueue to rq
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        q = Queue("parsing", connection=redis_conn)
        # Import dynamically to avoid circular import issues in router
        from app.workers.parsing_worker import parse_schema_job
        q.enqueue(parse_schema_job, str(pipeline_id))
    except Exception as e:
        job.status = "FAILED"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")
        
    return {"status": "STARTED"}
    
@router.get("/pipelines")
async def list_pipelines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all pipelines."""
    # Simplified version for MVP, should use a repo pattern
    from sqlalchemy import select
    result = await db.execute(select(PipelineJob).order_by(PipelineJob.created_at.desc()))
    pipelines = result.scalars().all()
    
    return [
        {
            "id": str(p.id),
            "status": p.status,
            "created_at": p.created_at,
            "total_chunks": p.total_chunks,
            "completed_chunks": p.completed_chunks,
        }
        for p in pipelines
    ]

@router.get("/pipelines/{pipeline_id}")
async def get_pipeline(
    pipeline_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single pipeline stats."""
    job = await db.get(PipelineJob, pipeline_id)
    if not job:
        raise HTTPException(status_code=404, detail="Pipeline not found")
        
    return {
        "id": str(job.id),
        "status": job.status,
        "created_at": job.created_at,
        "total_chunks": job.total_chunks,
        "completed_chunks": job.completed_chunks,
    }

@router.get("/pipelines/{pipeline_id}/chunks")
async def get_pipeline_chunks(
    pipeline_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chunks for a pipeline."""
    from sqlalchemy import select
    from app.models.chunk_task import ChunkTask
    
    result = await db.execute(
        select(ChunkTask)
        .where(ChunkTask.pipeline_id == pipeline_id)
        .order_by(ChunkTask.sequence_num)
    )
    chunks = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(c.id),
                "object_type": c.object_type,
                "object_name": c.object_name,
                "status": c.status,
                "stage": c.stage,
                "sequence_num": c.sequence_num
            }
            for c in chunks
        ],
        "total": len(chunks)
    }

@router.get("/chunks/{chunk_id}/artifact")
async def get_chunk_artifact(
    chunk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get original and converted SQL for an artifact."""
    from sqlalchemy import select
    from app.models.artifact import Artifact
    
    result = await db.execute(
        select(Artifact).where(Artifact.chunk_id == chunk_id)
    )
    artifact = result.scalars().first()
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    return {
        "id": str(artifact.id),
        "chunk_id": str(artifact.chunk_id),
        "original_sql": artifact.original_sql,
        "converted_sql": artifact.converted_sql,
        "version": artifact.version
    }

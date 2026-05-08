"""Tests for background workers."""

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.project import Project
from app.models.pipeline_job import PipelineJob
from app.models.chunk_task import ChunkTask
from app.workers.parsing_worker import parse_ddl_job

engine = create_engine("sqlite:///:memory:")
TestSession = sessionmaker(bind=engine)

def setup_function():
    Base.metadata.create_all(engine)

def teardown_function():
    Base.metadata.drop_all(engine)


def test_parsing_worker_integration():
    """Test that parsing worker correctly parses DB2 file and stores chunks in DB."""
    db = TestSession()
    
    # 1. Setup DB state
    user = User(username="testuser", email="t@test.com", password_hash="pw")
    db.add(user)
    db.commit()
    
    project = Project(name="Test", created_by=user.id)
    db.add(project)
    db.commit()
    
    job_id = str(uuid.uuid4())
    job = PipelineJob(
        id=job_id,
        project_id=project.id,
        created_by=user.id,
        status="created",
        original_file_path="tests/fixtures/sample_ddl/db2_sample.sql"
    )
    db.add(job)
    db.commit()
    
    # 2. To test the worker, since job_context creates its own SessionLocal,
    # and sqlite :memory: DBs don't share data across sessions unless connected to the same engine
    # We must patch SessionLocal in app.workers.base_worker to use our TestSession
    import app.workers.base_worker
    original_session = app.workers.base_worker.SessionLocal
    app.workers.base_worker.SessionLocal = TestSession
    
    try:
        # Run the worker function
        parse_ddl_job(uuid.UUID(job_id))
        
        # 3. Assertions
        db.expire_all()
        updated_job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
        
        assert updated_job.status == "parsed"
        assert updated_job.total_chunks > 0
        
        # Fetch tasks
        tasks = db.query(ChunkTask).filter(ChunkTask.job_id == job_id).all()
        assert len(tasks) == updated_job.total_chunks
        assert tasks[0].status == "pending"
    finally:
        # Restore
        app.workers.base_worker.SessionLocal = original_session
        db.close()

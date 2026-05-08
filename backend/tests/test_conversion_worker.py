"""Integration tests for conversion worker."""

import pytest
import uuid
from datetime import datetime, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.pipeline_job import PipelineJob
from app.models.chunk_task import ChunkTask
from app.models.project import Project
from app.models.user import User
from app.workers.conversion_worker import convert_chunk_job

engine = create_engine("sqlite:///:memory:")
TestSession = sessionmaker(bind=engine)

def setup_function():
    Base.metadata.create_all(engine)

def teardown_function():
    Base.metadata.drop_all(engine)

def test_conversion_worker_integration():
    """Test that the conversion worker properly updates tasks."""
    db_session = TestSession()
    
    # 1. Setup DB state
    user = User(username="testuser", email="t@test.com", password_hash="pw")
    db_session.add(user)
    db_session.commit()
    
    project = Project(name="Test", created_by=user.id)
    db_session.add(project)
    db_session.commit()
    
    job = PipelineJob(
        id=str(uuid.uuid4()),
        project_id=project.id,
        created_by=user.id,
        original_file_path="test.sql",
        total_chunks=2,
        status="running"
    )
    db_session.add(job)
    db_session.commit()
    
    # Task 1: Table (should be deterministic)
    task1 = ChunkTask(
        id=str(uuid.uuid4()),
        job_id=job.id,
        object_name="T1",
        object_type="TABLE",
        original_sql="CREATE TABLE T1 (ID INT GENERATED ALWAYS AS IDENTITY) IN TS1;",
        status="pending"
    )
    # Task 2: Procedure (should need AI)
    task2 = ChunkTask(
        id=str(uuid.uuid4()),
        job_id=job.id,
        object_name="P1",
        object_type="PROCEDURE",
        original_sql="CREATE PROCEDURE P1() BEGIN END;",
        status="pending"
    )
    
    db_session.add_all([task1, task2])
    db_session.commit()

    import app.workers.base_worker
    original_session = app.workers.base_worker.SessionLocal
    app.workers.base_worker.SessionLocal = TestSession

    try:
        # 2. Run Worker on Task 1
        convert_chunk_job(uuid.UUID(job.id), task1.id)
        
        db_session.refresh(task1)
        db_session.refresh(job)
        
        assert task1.status == "converted"
        assert "IDENTITY(1,1)" in task1.converted_sql
        assert "IN TS1" not in task1.converted_sql
        assert job.completed_chunks == 1
        assert task1.conversion_method == "deterministic"
        assert task1.completed_at is not None

        # 3. Run Worker on Task 2
        convert_chunk_job(uuid.UUID(job.id), task2.id)
        
        db_session.refresh(task2)
        db_session.refresh(job)
        
        assert task2.status == "needs_ai"
        assert task2.converted_sql is None
        assert task2.conversion_method is None
        assert job.completed_chunks == 1  # unchanged for needs_ai
    finally:
        app.workers.base_worker.SessionLocal = original_session
        db_session.close()

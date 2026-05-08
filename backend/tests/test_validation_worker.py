"""Integration tests for validation worker."""

import pytest
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.pipeline_job import PipelineJob
from app.models.chunk_task import ChunkTask
from app.models.project import Project
from app.models.user import User
from app.models.validation_result import ValidationResult
from app.workers.validation_worker import validate_chunk_job

engine = create_engine("sqlite:///:memory:")
TestSession = sessionmaker(bind=engine)

def setup_function():
    Base.metadata.create_all(engine)

def teardown_function():
    Base.metadata.drop_all(engine)

def test_validation_worker_success(monkeypatch):
    """Test worker handles successful validation."""
    monkeypatch.setenv("TESTING", "1")
    db_session = TestSession()
    
    # Setup
    user = User(username="v_testuser", email="v@test.com", password_hash="pw")
    db_session.add(user)
    db_session.commit()
    project = Project(name="TestV", created_by=user.id)
    db_session.add(project)
    db_session.commit()
    job = PipelineJob(id=str(uuid.uuid4()), project_id=project.id, created_by=user.id, original_file_path="t.sql", status="running")
    db_session.add(job)
    db_session.commit()
    
    task = ChunkTask(id=str(uuid.uuid4()), job_id=job.id, object_name="T1", object_type="TABLE", original_sql="CREATE TABLE T1();", converted_sql="CREATE TABLE T1();", status="converted")
    db_session.add(task)
    db_session.commit()

    import app.workers.base_worker
    original_session = app.workers.base_worker.SessionLocal
    app.workers.base_worker.SessionLocal = TestSession

    try:
        validate_chunk_job(uuid.UUID(job.id), task.id)
        
        db_session.refresh(task)
        assert task.status == "validated"
        
        results = db_session.query(ValidationResult).filter_by(task_id=task.id).all()
        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].error_code is None
        
    finally:
        app.workers.base_worker.SessionLocal = original_session
        db_session.close()

def test_validation_worker_failure_retry(monkeypatch):
    """Test worker handles failed validation and updates retry logic."""
    monkeypatch.setenv("TESTING", "1")
    db_session = TestSession()
    
    # Setup
    user = User(username="v2_testuser", email="v2@test.com", password_hash="pw")
    db_session.add(user)
    db_session.commit()
    project = Project(name="TestV2", created_by=user.id)
    db_session.add(project)
    db_session.commit()
    job = PipelineJob(id=str(uuid.uuid4()), project_id=project.id, created_by=user.id, original_file_path="t.sql", status="running")
    db_session.add(job)
    db_session.commit()
    
    task = ChunkTask(id=str(uuid.uuid4()), job_id=job.id, object_name="T1", object_type="TABLE", original_sql="bad", converted_sql="FAIL_SYNTAX", status="converted", retry_count=0)
    db_session.add(task)
    db_session.commit()

    import app.workers.base_worker
    original_session = app.workers.base_worker.SessionLocal
    app.workers.base_worker.SessionLocal = TestSession

    try:
        validate_chunk_job(uuid.UUID(job.id), task.id)
        
        db_session.refresh(task)
        assert task.status == "needs_ai"
        assert task.retry_count == 1
        
        results = db_session.query(ValidationResult).filter_by(task_id=task.id).all()
        assert len(results) == 1
        assert results[0].passed is False
        assert results[0].error_code == "42000"
        
    finally:
        app.workers.base_worker.SessionLocal = original_session
        db_session.close()

def test_validation_worker_failure_max_retries(monkeypatch):
    """Test worker handles failure when max retries exceeded."""
    monkeypatch.setenv("TESTING", "1")
    db_session = TestSession()
    
    # Setup
    user = User(username="v3_user", email="v3@test.com", password_hash="pw")
    db_session.add(user)
    db_session.commit()
    project = Project(name="TestV3", created_by=user.id)
    db_session.add(project)
    db_session.commit()
    job = PipelineJob(id=str(uuid.uuid4()), project_id=project.id, created_by=user.id, original_file_path="t.sql", status="running")
    db_session.add(job)
    db_session.commit()
    
    # Set retry_count to 3 (max is 3 in worker)
    task = ChunkTask(id=str(uuid.uuid4()), job_id=job.id, object_name="T1", object_type="TABLE", original_sql="bad", converted_sql="FAIL_SYNTAX", status="converted", retry_count=3)
    db_session.add(task)
    db_session.commit()

    import app.workers.base_worker
    original_session = app.workers.base_worker.SessionLocal
    app.workers.base_worker.SessionLocal = TestSession

    try:
        validate_chunk_job(uuid.UUID(job.id), task.id)
        
        db_session.refresh(task)
        assert task.status == "failed_validation"
        assert task.retry_count == 4
        assert "Validation failed after 3 retries" in task.error_message
        
    finally:
        app.workers.base_worker.SessionLocal = original_session
        db_session.close()

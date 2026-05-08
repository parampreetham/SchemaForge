"""Integration tests for AI worker."""

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
from app.models.ai_interaction import AIInteraction
from app.workers.ai_worker import translate_chunk_job

engine = create_engine("sqlite:///:memory:")
TestSession = sessionmaker(bind=engine)

def setup_function():
    Base.metadata.create_all(engine)

def teardown_function():
    Base.metadata.drop_all(engine)

def test_ai_worker_integration(monkeypatch):
    """Test that the AI worker correctly logs interaction and updates task."""
    monkeypatch.setenv("TESTING", "1")
    
    db_session = TestSession()
    
    # Setup DB
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
        total_chunks=1,
        status="running"
    )
    db_session.add(job)
    db_session.commit()
    
    task1 = ChunkTask(
        id=str(uuid.uuid4()),
        job_id=job.id,
        object_name="P1",
        object_type="PROCEDURE",
        original_sql="CREATE PROCEDURE P1() BEGIN END;",
        status="needs_ai"
    )
    db_session.add(task1)
    db_session.commit()

    import app.workers.base_worker
    original_session = app.workers.base_worker.SessionLocal
    app.workers.base_worker.SessionLocal = TestSession

    try:
        # Run Worker
        translate_chunk_job(uuid.UUID(job.id), task1.id)
        
        db_session.refresh(task1)
        db_session.refresh(job)
        
        assert task1.status == "translated"
        assert task1.converted_sql == "CREATE PROCEDURE P1 AS\nBEGIN\nEND;"
        assert job.completed_chunks == 1
        assert "ai (" in task1.conversion_method
        assert task1.completed_at is not None
        
        # Verify AIInteraction was created
        interactions = db_session.query(AIInteraction).filter(AIInteraction.task_id == task1.id).all()
        assert len(interactions) == 1
        
        interaction = interactions[0]
        assert interaction.attempt_number == 1
        assert interaction.model == "gpt-4o"
        assert interaction.cost_usd >= 0
        assert interaction.latency_ms > 0
        
    finally:
        app.workers.base_worker.SessionLocal = original_session
        db_session.close()

"""Tests for SQLAlchemy ORM models."""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.chunk_task import ChunkTask
from app.models.pipeline_job import PipelineJob
from app.models.project import Project
from app.models.user import User
from app.models.worker_heartbeat import WorkerHeartbeat

# Use in-memory SQLite for tests
engine = create_engine("sqlite:///:memory:")
TestSession = sessionmaker(bind=engine)


def setup_function():
    """Create all tables before each test."""
    Base.metadata.create_all(engine)


def teardown_function():
    """Drop all tables after each test."""
    Base.metadata.drop_all(engine)


def test_user_creation():
    """Test creating a user with required fields."""
    db = TestSession()
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_pw",
        role="operator",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.role == "operator"
    assert user.is_active is True
    db.close()


def test_user_unique_username():
    """Test that duplicate usernames raise an error."""
    db = TestSession()
    user1 = User(username="unique_user", email="a@test.com", password_hash="pw1")
    user2 = User(username="unique_user", email="b@test.com", password_hash="pw2")
    db.add(user1)
    db.commit()
    db.add(user2)
    try:
        db.commit()
        pytest.fail("Should have raised integrity error")
    except Exception:
        db.rollback()
    db.close()


def test_project_creation():
    """Test creating a project linked to a user."""
    db = TestSession()
    user = User(username="projowner", email="proj@test.com", password_hash="pw")
    db.add(user)
    db.commit()

    project = Project(
        name="Test Migration",
        source_db_type="db2",
        target_db_type="azure_sql",
        created_by=user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    assert project.id is not None
    assert project.name == "Test Migration"
    assert project.created_by == user.id
    assert project.is_archived is False
    db.close()


def test_pipeline_job_creation():
    """Test creating a pipeline job with progress fields."""
    db = TestSession()
    user = User(username="pipeowner", email="pipe@test.com", password_hash="pw")
    db.add(user)
    db.commit()

    project = Project(name="Pipe Project", created_by=user.id)
    db.add(project)
    db.commit()

    job = PipelineJob(
        project_id=project.id,
        status="created",
        total_chunks=100,
        created_by=user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    assert job.id is not None
    assert job.status == "created"
    assert job.total_chunks == 100
    assert job.completed_chunks == 0
    assert job.cancel_requested is False
    db.close()


def test_chunk_task_creation():
    """Test creating a chunk task with SQL content."""
    db = TestSession()
    user = User(username="chunkowner", email="chunk@test.com", password_hash="pw")
    db.add(user)
    db.commit()

    project = Project(name="Chunk Project", created_by=user.id)
    db.add(project)
    db.commit()

    job = PipelineJob(project_id=project.id, created_by=user.id)
    db.add(job)
    db.commit()

    chunk = ChunkTask(
        job_id=job.id,
        object_name="EMPLOYEE",
        object_type="TABLE",
        original_sql="CREATE TABLE EMPLOYEE (...)",
        dependency_order=1,
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    assert chunk.id is not None
    assert chunk.object_name == "EMPLOYEE"
    assert chunk.object_type == "TABLE"
    assert chunk.status == "pending"
    assert chunk.retry_count == 0
    db.close()


def test_worker_heartbeat_creation():
    """Test creating a worker heartbeat record."""
    db = TestSession()
    heartbeat = WorkerHeartbeat(
        worker_id="parsing-worker-1",
        queue_name="parsing",
        status="idle",
        pid=12345,
        hostname="DESKTOP-001",
    )
    db.add(heartbeat)
    db.commit()
    db.refresh(heartbeat)

    assert heartbeat.worker_id == "parsing-worker-1"
    assert heartbeat.queue_name == "parsing"
    assert heartbeat.status == "idle"
    db.close()


def test_pipeline_project_relationship():
    """Test that pipeline navigates to project via relationship."""
    db = TestSession()
    user = User(username="relowner", email="rel@test.com", password_hash="pw")
    db.add(user)
    db.commit()

    project = Project(name="Rel Project", created_by=user.id)
    db.add(project)
    db.commit()

    job = PipelineJob(project_id=project.id, created_by=user.id)
    db.add(job)
    db.commit()
    db.refresh(job)

    assert job.project.name == "Rel Project"
    assert job in project.pipeline_jobs
    db.close()

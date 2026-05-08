"""Chunk task model."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChunkTask(Base):
    """An individual DB object conversion task within a pipeline."""

    __tablename__ = "chunk_tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("pipeline_jobs.id"), nullable=False, index=True
    )
    object_name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    conversion_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    original_sql: Mapped[str] = mapped_column(Text, nullable=False)
    converted_sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    dependency_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dependencies: Mapped[str | None] = mapped_column(Text, nullable=True, default="[]")
    worker_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(UTC)
    )

    # Relationships
    pipeline_job = relationship("PipelineJob", back_populates="chunk_tasks", lazy="select")
    artifacts = relationship("Artifact", back_populates="chunk_task", lazy="select")
    ai_interactions = relationship("AIInteraction", back_populates="chunk_task", lazy="select")
    validation_results = relationship(
        "ValidationResult", back_populates="chunk_task", lazy="select"
    )
    log_entries = relationship("LogEntry", back_populates="chunk_task", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<ChunkTask(id={self.id}, object={self.object_name}, "
            f"type={self.object_type}, status={self.status})>"
        )

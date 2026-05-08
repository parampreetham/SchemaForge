"""Log entry model."""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LogEntry(Base):
    """Structured log entry persisted in the database."""

    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False)
    job_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("pipeline_jobs.id"), nullable=True, index=True
    )
    task_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("chunk_tasks.id"), nullable=True, index=True
    )
    log_level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    worker_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(UTC), index=True
    )

    # Relationships
    pipeline_job = relationship("PipelineJob", back_populates="log_entries", lazy="select")
    chunk_task = relationship("ChunkTask", back_populates="log_entries", lazy="select")

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, level={self.log_level}, stage={self.stage})>"

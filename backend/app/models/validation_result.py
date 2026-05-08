"""Validation result model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ValidationResult(Base):
    """Result of validating generated SQL against Azure SQL."""

    __tablename__ = "validation_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chunk_tasks.id"), nullable=False, index=True
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validated_sql: Mapped[str] = mapped_column(Text, nullable=False)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(UTC)
    )

    # Relationships
    chunk_task = relationship("ChunkTask", back_populates="validation_results", lazy="select")

    def __repr__(self) -> str:
        return f"<ValidationResult(id={self.id}, passed={self.passed})>"

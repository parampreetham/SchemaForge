"""Project model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    """A migration project containing pipelines."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_db_type: Mapped[str] = mapped_column(String(50), nullable=False, default="db2")
    target_db_type: Mapped[str] = mapped_column(String(50), nullable=False, default="azure_sql")
    source_db_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    creator = relationship("User", back_populates="projects", lazy="select")
    pipeline_jobs = relationship("PipelineJob", back_populates="project", lazy="select")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name})>"

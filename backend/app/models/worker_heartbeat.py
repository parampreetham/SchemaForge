"""Worker heartbeat model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkerHeartbeat(Base):
    """Worker health tracking via periodic heartbeats."""

    __tablename__ = "worker_heartbeats"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    worker_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    queue_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="idle")
    current_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    pid: Mapped[int] = mapped_column(Integer, nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    last_heartbeat: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(UTC), index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(UTC)
    )

    def __repr__(self) -> str:
        return f"<WorkerHeartbeat(worker_id={self.worker_id}, status={self.status})>"

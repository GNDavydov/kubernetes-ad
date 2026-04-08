import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class DetectMetricModel(Base):
    __tablename__ = "detect_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    processed_events: Mapped[int] = mapped_column(Integer, nullable=False)
    anomalies_count: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now(timezone.utc)
    )
    start_timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False)
    end_timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    task = relationship("TaskModel", back_populates="detect_metrics")

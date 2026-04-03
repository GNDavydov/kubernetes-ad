import uuid

from sqlalchemy import (
    Integer, Float, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class TaskResultModel(Base):
    __tablename__ = "task_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), unique=True)

    processed_events: Mapped[int] = mapped_column(Integer)
    anomalies_count: Mapped[int] = mapped_column(Integer)

    duration: Mapped[float] = mapped_column(Float)

    task = relationship("TaskModel", back_populates="result")

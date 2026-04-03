import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String, Integer, Float, TIMESTAMP, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.model_status import ModelStatus
from app.infrastructure.db.models.base import Base


class ModelModel(Base):
    __tablename__ = "models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus, name="model_status_enum"),
        nullable=False
    )

    input_dim: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seq_len: Mapped[int] = mapped_column(Integer, nullable=False)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)

    model_path: Mapped[str | None] = mapped_column(String, nullable=True)

    last_processed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now(timezone.utc))

    tasks = relationship("TaskModel", back_populates="model")
    metrics = relationship("TrainingMetricModel", back_populates="model")

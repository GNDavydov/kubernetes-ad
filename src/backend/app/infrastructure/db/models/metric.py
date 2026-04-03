import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Integer, Float, TIMESTAMP, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base


class TrainingMetricModel(Base):
    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("models.id", ondelete="CASCADE"))

    epoch: Mapped[int] = mapped_column(Integer)
    loss: Mapped[float] = mapped_column(Float)
    val_loss: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now(timezone.utc))

    model = relationship("ModelModel", back_populates="metrics")

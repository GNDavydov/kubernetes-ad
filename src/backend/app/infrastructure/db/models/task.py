import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Enum, Text, TIMESTAMP, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType
from app.infrastructure.db.models.base import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    type: Mapped[TaskType] = mapped_column(
        Enum(TaskType, name="task_type_enum"),
        nullable=False
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status_enum"),
        nullable=False
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("models.id", ondelete="CASCADE"))
    integration_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("integrations.id", ondelete="CASCADE"))

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now(timezone.utc))
    started_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True)

    model = relationship("ModelModel", back_populates="tasks")
    integration = relationship("IntegrationModel", back_populates="tasks")
    result = relationship(
        "TaskResultModel", back_populates="task", uselist=False)

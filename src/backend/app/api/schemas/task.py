from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType


class CreateTaskRequest(BaseModel):
    type: TaskType
    model_id: UUID
    integration_id: UUID
    epochs: int | None = None

    @model_validator(mode="after")
    def validate_epochs(self) -> "CreateTaskRequest":
        if self.type == TaskType.TRAIN and self.epochs is None:
            raise ValueError("epochs is required for train tasks")
        if self.type == TaskType.DETECT and self.epochs is not None:
            raise ValueError("epochs must be omitted for detect tasks")
        return self


class TaskResponse(BaseModel):
    id: UUID
    model_id: UUID
    integration_id: UUID
    user_id: UUID
    type: TaskType
    status: TaskStatus
    epochs: int | None
    created_at: datetime | None


class TrainMetricResponse(BaseModel):
    id: UUID
    task_id: UUID
    processed_events: int
    epoch: int
    loss: float
    val_loss: float
    duration: float
    created_at: datetime | None


class DetectMetricResponse(BaseModel):
    id: UUID
    task_id: UUID
    processed_events: int
    anomalies_count: int
    duration: float
    created_at: datetime | None
    start_timestamp: datetime
    end_timestamp: datetime

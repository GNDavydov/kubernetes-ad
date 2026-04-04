from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType


class TaskReadSchema(BaseModel):
    id: UUID
    type: TaskType
    status: TaskStatus
    model_id: UUID
    integration_id: UUID
    error: str
    created_at: datetime
    started_at: datetime
    finished_at: datetime

    model_config = ConfigDict(from_attributes=True)

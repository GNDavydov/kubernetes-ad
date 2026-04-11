from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType


@dataclass
class Task:
    id: UUID | None
    model_id: UUID
    integration_id: UUID
    user_id: UUID
    type: TaskType
    status: TaskStatus
    epochs: int | None
    created_at: datetime | None

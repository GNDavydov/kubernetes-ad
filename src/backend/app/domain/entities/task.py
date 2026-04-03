from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType


@dataclass
class Task:
    id: UUID
    type: TaskType
    status: TaskStatus
    model_id: UUID
    integration_id: UUID
    error: str
    created_at: datetime
    started_at: datetime
    finished_at: datetime

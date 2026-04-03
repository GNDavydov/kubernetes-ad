from dataclasses import dataclass
from uuid import UUID


@dataclass
class TaskResult:
    id: UUID
    task_id: UUID
    processed_events: int
    anomalies_count: int
    duration: float

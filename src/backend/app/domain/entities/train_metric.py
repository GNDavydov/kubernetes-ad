from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class TrainMetric:
    id: UUID | None
    task_id: UUID
    processed_events: int
    epoch: int
    loss: float
    val_loss: float
    duration: float
    created_at: datetime | None

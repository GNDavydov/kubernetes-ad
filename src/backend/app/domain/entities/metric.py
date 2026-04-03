from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class TrainingMetric:
    id: UUID
    model_id: UUID
    epoch: int
    loss: float
    val_loss: float
    created_at: datetime

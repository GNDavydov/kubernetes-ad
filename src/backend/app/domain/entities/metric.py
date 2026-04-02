from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrainingMetric:
    id: int
    model_id: int
    epoch: int
    loss: float
    val_loss: float
    created_at: datetime

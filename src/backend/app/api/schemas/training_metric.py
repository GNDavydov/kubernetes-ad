from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TrainingMetricReadSchema(BaseModel):
    id: UUID
    model_id: UUID
    epoch: int
    loss: float
    val_loss: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

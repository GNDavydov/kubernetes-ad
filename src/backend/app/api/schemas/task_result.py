from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskResultReadSchema(BaseModel):
    id: UUID
    task_id: UUID
    processed_events: int
    anomalies_count: int
    duration: float

    model_config = ConfigDict(from_attributes=True)

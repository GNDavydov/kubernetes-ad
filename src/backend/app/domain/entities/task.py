from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    id: int
    type: str
    model_id: int
    integration_id: int
    created_at: datetime
    started_at: datetime
    finished_at: datetime

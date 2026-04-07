from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class DetectMetrics:
    id: UUID | None
    task_id: UUID
    processed_events: int
    anomalies_count: int
    duration: float
    created_at: datetime | None
    start_timestamp: datetime
    end_timestamp: datetime

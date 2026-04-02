from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskResult:
    id: int
    task_id: int
    processed_events: int
    anomalies_count: int
    duration: float

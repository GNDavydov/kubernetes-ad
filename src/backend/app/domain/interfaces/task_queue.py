from uuid import UUID
from typing import Protocol


class TaskQueue(Protocol):
    def detect_task(task_id: UUID) -> None:
        ...

    def train_task(task_id: UUID) -> None:
        ...

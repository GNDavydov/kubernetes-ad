from uuid import UUID
from typing import Protocol


class TaskQueue(Protocol):
    def detect_task(self, task_id: UUID | str) -> None:
        ...

    def train_task(self, task_id: UUID | str) -> None:
        ...

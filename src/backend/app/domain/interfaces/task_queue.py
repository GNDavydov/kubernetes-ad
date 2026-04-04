from uuid import UUID
from typing import Protocol


class TaskQueue(Protocol):
    def detect_task(model_id: UUID, integration_id: UUID) -> None:
        ...

    def train_task(model_id: UUID, integration_id: UUID) -> None:
        ...

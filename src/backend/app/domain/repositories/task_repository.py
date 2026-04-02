from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from app.domain.entities.task import Task


class TaskRepository(ABC):

    @abstractmethod
    def add(self, task: Task) -> Task:
        ...

    @abstractmethod
    def list(self) -> List[Task]:
        ...

    @abstractmethod
    def list_by_model(self, model_id: int) -> List[Task]:
        ...

    @abstractmethod
    def list_by_integration(self, integration_id: int) -> List[Task]:
        ...

    @abstractmethod
    def finish(self, task_id: int, finished_at: datetime, started_at: datetime) -> Task | None:
        ...

    @abstractmethod
    def get_by_id(self, task_id: int) -> Task | None:
        ...

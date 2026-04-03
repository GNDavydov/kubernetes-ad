from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from app.domain.entities.task import Task


class TaskRepository(ABC):

    @abstractmethod
    async def add(self, task: Task) -> Task:
        ...

    @abstractmethod
    async def list(self) -> List[Task]:
        ...

    @abstractmethod
    async def list_by_model(self, model_id: UUID) -> List[Task]:
        ...

    @abstractmethod
    async def list_by_integration(self, integration_id: UUID) -> List[Task]:
        ...

    @abstractmethod
    async def finish(self, task_id: UUID, finished_at: datetime, started_at: datetime) -> Task | None:
        ...

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Task | None:
        ...

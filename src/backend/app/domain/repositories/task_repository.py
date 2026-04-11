from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.task import Task
from app.domain.enums.task_status import TaskStatus


class TaskRepository(ABC):

    @abstractmethod
    async def create(self, task: Task) -> Task:
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
    async def list_by_user(self, user_id: UUID) -> List[Task]:
        ...

    @abstractmethod
    async def update(self, task: Task) -> Task:
        ...

    @abstractmethod
    async def update_status(self, task_id: UUID, status: TaskStatus) -> Task | None:
        ...

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Task | None:
        ...

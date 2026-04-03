from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.task_result import TaskResult


class TaskResultRepository(ABC):

    @abstractmethod
    async def add(self, task_result: TaskResult) -> TaskResult:
        ...

    @abstractmethod
    async def list(self) -> List[TaskResult]:
        ...

    @abstractmethod
    async def get_by_id(self, task_result_id: UUID) -> TaskResult | None:
        ...

    @abstractmethod
    async def get_by_task(self, task_id: UUID) -> TaskResult | None:
        ...

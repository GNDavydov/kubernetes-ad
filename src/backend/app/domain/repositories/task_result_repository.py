from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.task_result import TaskResult


class TaskResultRepository(ABC):

    @abstractmethod
    def add(self, task_result: TaskResult) -> TaskResult:
        ...

    @abstractmethod
    def list(self) -> List[TaskResult]:
        ...

    @abstractmethod
    def get_by_id(self, task_result_id: int) -> TaskResult | None:
        ...

    @abstractmethod
    def get_by_task(self, task_id: int) -> TaskResult | None:
        ...

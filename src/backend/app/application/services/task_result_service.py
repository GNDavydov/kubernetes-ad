from uuid import UUID
from typing import List

from app.application.exceptions import ResourceNotFoundError
from app.domain.entities.task_result import TaskResult
from app.domain.repositories.task_result_repository import TaskResultRepository


class TaskResultService:
    def __init__(self, repository: TaskResultRepository) -> None:
        self._repository = repository

    async def list_all(self) -> List[TaskResult]:
        return await self._repository.list()

    async def get(self, task_result_id: UUID) -> TaskResult:
        result = await self._repository.get_by_id(task_result_id)
        if result is None:
            raise ResourceNotFoundError("Task result not found")
        return result

    async def get_by_task(self, task_id: UUID) -> TaskResult:
        result = await self._repository.get_by_task(task_id)
        if result is None:
            raise ResourceNotFoundError("Task result not found")
        return result

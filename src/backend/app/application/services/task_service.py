from uuid import UUID
from typing import List

from app.application.exceptions import ResourceNotFoundError
from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    async def list_all(self) -> List[Task]:
        return await self._repository.list()

    async def list_by_model(self, model_id: UUID) -> List[Task]:
        return await self._repository.list_by_model(model_id)

    async def list_by_integration(self, integration_id: UUID) -> List[Task]:
        return await self._repository.list_by_integration(integration_id)

    async def get(self, task_id: UUID) -> Task:
        task = await self._repository.get_by_id(task_id)
        if task is None:
            raise ResourceNotFoundError("Task not found")
        return task

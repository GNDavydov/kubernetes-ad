from uuid import UUID

from app.application.exceptions import ResourceNotFoundError
from app.domain.entities.task import Task
from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType
from app.domain.repositories.integration_repository import IntegrationRepository
from app.domain.repositories.model_repository import ModelRepository
from app.domain.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        model_repository: ModelRepository,
        integration_repository: IntegrationRepository,
    ) -> None:
        self._task_repository = task_repository
        self._model_repository = model_repository
        self._integration_repository = integration_repository

    async def create(
        self,
        user_id: UUID,
        model_id: UUID,
        integration_id: UUID,
        type: TaskType,
        epochs: int | None,
    ) -> Task:
        await self._ensure_owned_model(user_id=user_id, model_id=model_id)
        await self._ensure_owned_integration(
            user_id=user_id,
            integration_id=integration_id,
        )

        task = Task(
            id=None,
            model_id=model_id,
            integration_id=integration_id,
            user_id=user_id,
            type=type,
            status=TaskStatus.STARTING,
            epochs=epochs,
            created_at=None,
        )
        return await self._task_repository.create(task)

    async def list_my(self, user_id: UUID) -> list[Task]:
        return await self._task_repository.list_by_user(user_id)

    async def get_my_by_id(self, user_id: UUID, task_id: UUID) -> Task:
        task = await self._task_repository.get_by_id(task_id)
        if task is None or task.user_id != user_id:
            raise ResourceNotFoundError("Task not found")
        return task

    async def _ensure_owned_model(self, user_id: UUID, model_id: UUID) -> None:
        model = await self._model_repository.get_by_id(model_id)
        if model is None or model.user_id != user_id:
            raise ResourceNotFoundError("Model not found")

    async def _ensure_owned_integration(
        self,
        user_id: UUID,
        integration_id: UUID,
    ) -> None:
        integration = await self._integration_repository.get_by_id(integration_id)
        if integration is None or integration.user_id != user_id:
            raise ResourceNotFoundError("Integration not found")

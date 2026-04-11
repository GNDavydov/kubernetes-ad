from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task import Task
from app.domain.enums.task_status import TaskStatus
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.db.models.task import TaskModel


class TaskRepositoryImpl(TaskRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, task: Task) -> Task:
        db_task = TaskModel(
            model_id=task.model_id,
            integration_id=task.integration_id,
            user_id=task.user_id,
            type=task.type,
            status=task.status,
            created_at=task.created_at or datetime.now(timezone.utc),
            epochs=task.epochs,
        )
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return self._to_entity(db_task)

    async def list(self) -> List[Task]:
        result = await self.db.execute(select(TaskModel))
        db_tasks = result.scalars().all()
        return [self._to_entity(db_task) for db_task in db_tasks]

    async def list_by_model(self, model_id: UUID) -> List[Task]:
        result = await self.db.execute(
            select(TaskModel).where(TaskModel.model_id == model_id)
        )
        db_tasks = result.scalars().all()
        return [self._to_entity(db_task) for db_task in db_tasks]

    async def list_by_integration(self, integration_id: UUID) -> List[Task]:
        result = await self.db.execute(
            select(TaskModel).where(TaskModel.integration_id == integration_id)
        )
        db_tasks = result.scalars().all()
        return [self._to_entity(db_task) for db_task in db_tasks]

    async def list_by_user(self, user_id: UUID) -> List[Task]:
        result = await self.db.execute(
            select(TaskModel).where(TaskModel.user_id == user_id)
        )
        db_tasks = result.scalars().all()
        return [self._to_entity(db_task) for db_task in db_tasks]

    async def update(self, task: Task) -> Task:
        if task.id is None:
            raise ValueError("Task id is required for update")
        db_task = await self.db.get(TaskModel, task.id)
        if db_task is None:
            raise ValueError(f"Task with id={task.id} not found")

        db_task.model_id = task.model_id
        db_task.integration_id = task.integration_id
        db_task.user_id = task.user_id
        db_task.type = task.type
        db_task.status = task.status
        db_task.epochs = task.epochs
        await self.db.commit()
        await self.db.refresh(db_task)
        return self._to_entity(db_task)

    async def update_status(self, task_id: UUID, status: TaskStatus) -> Task | None:
        db_task = await self.db.get(TaskModel, task_id)
        if db_task is None:
            return None

        db_task.status = status
        await self.db.commit()
        await self.db.refresh(db_task)
        return self._to_entity(db_task)

    async def get_by_id(self, task_id: UUID) -> Task | None:
        db_task = await self.db.get(TaskModel, task_id)
        return self._to_entity(db_task) if db_task else None

    @staticmethod
    def _to_entity(db_task: TaskModel) -> Task:
        return Task(
            id=db_task.id,
            model_id=db_task.model_id,
            integration_id=db_task.integration_id,
            user_id=db_task.user_id,
            type=db_task.type,
            status=db_task.status,
            epochs=db_task.epochs,
            created_at=db_task.created_at,
        )

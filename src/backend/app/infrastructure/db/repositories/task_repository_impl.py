from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.db.models.task import TaskModel


class TaskRepositoryImpl(TaskRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, task: Task) -> Task:
        db_task = TaskModel(
            type=task.type,
            status=task.status,
            model_id=task.model_id,
            integration_id=task.integration_id,
            error=task.error,
            created_at=task.created_at,
            started_at=task.started_at,
            finished_at=task.finished_at,
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

    async def finish(self, task_id: UUID, finished_at: datetime, started_at: datetime) -> Task | None:
        db_task = await self.db.get(TaskModel, task_id)
        if db_task is None:
            return None

        db_task.started_at = started_at
        db_task.finished_at = finished_at
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
            type=db_task.type,
            status=db_task.status,
            model_id=db_task.model_id,
            integration_id=db_task.integration_id,
            error=db_task.error or "",
            created_at=db_task.created_at,
            started_at=db_task.started_at or db_task.created_at,
            finished_at=db_task.finished_at or db_task.created_at,
        )

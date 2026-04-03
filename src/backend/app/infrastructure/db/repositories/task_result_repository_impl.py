from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task_result import TaskResult
from app.domain.repositories.task_result_repository import TaskResultRepository
from app.infrastructure.db.models.task_result import TaskResultModel


class TaskResultRepositoryImpl(TaskResultRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, task_result: TaskResult) -> TaskResult:
        db_task_result = TaskResultModel(
            task_id=task_result.task_id,
            processed_events=task_result.processed_events,
            anomalies_count=task_result.anomalies_count,
            duration=task_result.duration,
        )
        self.db.add(db_task_result)
        await self.db.commit()
        await self.db.refresh(db_task_result)
        return self._to_entity(db_task_result)

    async def list(self) -> List[TaskResult]:
        result = await self.db.execute(select(TaskResultModel))
        db_results = result.scalars().all()
        return [self._to_entity(db_result) for db_result in db_results]

    async def get_by_id(self, task_result_id: UUID) -> TaskResult | None:
        db_task_result = await self.db.get(TaskResultModel, task_result_id)
        return self._to_entity(db_task_result) if db_task_result else None

    async def get_by_task(self, task_id: UUID) -> TaskResult | None:
        result = await self.db.execute(
            select(TaskResultModel).where(TaskResultModel.task_id == task_id)
        )
        db_task_result = result.scalars().first()
        return self._to_entity(db_task_result) if db_task_result else None

    @staticmethod
    def _to_entity(db_task_result: TaskResultModel) -> TaskResult:
        return TaskResult(
            id=db_task_result.id,
            task_id=db_task_result.task_id,
            processed_events=db_task_result.processed_events,
            anomalies_count=db_task_result.anomalies_count,
            duration=db_task_result.duration,
        )

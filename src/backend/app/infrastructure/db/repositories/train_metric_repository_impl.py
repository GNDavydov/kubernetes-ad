from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.train_metric import TrainMetric
from app.domain.repositories.train_metric_repository import TrainMetricRepository
from app.infrastructure.db.models.train_metric import TrainMetricModel


class TrainMetricRepositoryImpl(TrainMetricRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, train_metric: TrainMetric) -> TrainMetric:
        db_metric = TrainMetricModel(
            task_id=train_metric.task_id,
            processed_events=train_metric.processed_events,
            epoch=train_metric.epoch,
            loss=train_metric.loss,
            val_loss=train_metric.val_loss,
            duration=train_metric.duration,
            created_at=train_metric.created_at or datetime.now(timezone.utc),
        )
        self.db.add(db_metric)
        await self.db.commit()
        await self.db.refresh(db_metric)
        return self._to_entity(db_metric)

    async def list(self) -> List[TrainMetric]:
        result = await self.db.execute(select(TrainMetricModel))
        db_metrics = result.scalars().all()
        return [self._to_entity(db_metric) for db_metric in db_metrics]

    async def list_by_task(self, task_id: UUID) -> List[TrainMetric]:
        result = await self.db.execute(
            select(TrainMetricModel).where(TrainMetricModel.task_id == task_id)
        )
        db_metrics = result.scalars().all()
        return [self._to_entity(db_metric) for db_metric in db_metrics]

    async def get_by_id(self, train_metric_id: UUID) -> TrainMetric | None:
        db_metric = await self.db.get(TrainMetricModel, train_metric_id)
        return self._to_entity(db_metric) if db_metric else None

    @staticmethod
    def _to_entity(db_metric: TrainMetricModel) -> TrainMetric:
        return TrainMetric(
            id=db_metric.id,
            task_id=db_metric.task_id,
            processed_events=db_metric.processed_events,
            epoch=db_metric.epoch,
            loss=db_metric.loss,
            val_loss=db_metric.val_loss,
            duration=db_metric.duration,
            created_at=db_metric.created_at,
        )

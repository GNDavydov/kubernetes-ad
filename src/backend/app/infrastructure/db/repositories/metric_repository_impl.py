from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.metric import TrainingMetric
from app.domain.repositories.metric_repository import TrainingMetricRepository
from app.infrastructure.db.models.metric import TrainingMetricModel


class TrainingMetricRepositoryImpl(TrainingMetricRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, metric: TrainingMetric) -> TrainingMetric:
        db_metric = TrainingMetricModel(
            model_id=metric.model_id,
            epoch=metric.epoch,
            loss=metric.loss,
            val_loss=metric.val_loss,
            created_at=metric.created_at,
        )
        self.db.add(db_metric)
        await self.db.commit()
        await self.db.refresh(db_metric)
        return self._to_entity(db_metric)

    async def list(self) -> List[TrainingMetric]:
        result = await self.db.execute(select(TrainingMetricModel))
        db_metrics = result.scalars().all()
        return [self._to_entity(db_metric) for db_metric in db_metrics]

    async def list_by_model(self, model_id: UUID) -> List[TrainingMetric]:
        result = await self.db.execute(
            select(TrainingMetricModel).where(
                TrainingMetricModel.model_id == model_id)
        )
        db_metrics = result.scalars().all()
        return [self._to_entity(db_metric) for db_metric in db_metrics]

    async def get_by_id(self, metric_id: UUID) -> TrainingMetric | None:
        db_metric = await self.db.get(TrainingMetricModel, metric_id)
        return self._to_entity(db_metric) if db_metric else None

    @staticmethod
    def _to_entity(db_metric: TrainingMetricModel) -> TrainingMetric:
        return TrainingMetric(
            id=db_metric.id,
            model_id=db_metric.model_id,
            epoch=db_metric.epoch,
            loss=db_metric.loss,
            val_loss=db_metric.val_loss,
            created_at=db_metric.created_at,
        )

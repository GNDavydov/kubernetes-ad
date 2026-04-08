from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.detect_metric import DetectMetric
from app.domain.repositories.detect_metric_repository import DetectMetricRepository
from app.infrastructure.db.models.detect_metric import DetectMetricModel


class DetectMetricRepositoryImpl(DetectMetricRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, detect_metric: DetectMetric) -> DetectMetric:
        db_detect_metric = DetectMetricModel(
            task_id=detect_metric.task_id,
            processed_events=detect_metric.processed_events,
            anomalies_count=detect_metric.anomalies_count,
            duration=detect_metric.duration,
            created_at=detect_metric.created_at or datetime.now(timezone.utc),
            start_timestamp=detect_metric.start_timestamp,
            end_timestamp=detect_metric.end_timestamp,
        )
        self.db.add(db_detect_metric)
        await self.db.commit()
        await self.db.refresh(db_detect_metric)
        return self._to_entity(db_detect_metric)

    async def list(self) -> List[DetectMetric]:
        result = await self.db.execute(select(DetectMetricModel))
        db_results = result.scalars().all()
        return [self._to_entity(db_result) for db_result in db_results]

    async def get_by_id(self, detect_metric_id: UUID) -> DetectMetric | None:
        db_detect_metric = await self.db.get(DetectMetricModel, detect_metric_id)
        return self._to_entity(db_detect_metric) if db_detect_metric else None

    async def list_by_task(self, task_id: UUID) -> List[DetectMetric]:
        result = await self.db.execute(
            select(DetectMetricModel).where(
                DetectMetricModel.task_id == task_id)
        )
        db_results = result.scalars().all()
        return [self._to_entity(db_result) for db_result in db_results]

    @staticmethod
    def _to_entity(db_detect_metric: DetectMetricModel) -> DetectMetric:
        return DetectMetric(
            id=db_detect_metric.id,
            task_id=db_detect_metric.task_id,
            processed_events=db_detect_metric.processed_events,
            anomalies_count=db_detect_metric.anomalies_count,
            duration=db_detect_metric.duration,
            created_at=db_detect_metric.created_at,
            start_timestamp=db_detect_metric.start_timestamp,
            end_timestamp=db_detect_metric.end_timestamp,
        )

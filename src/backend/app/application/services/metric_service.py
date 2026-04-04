from uuid import UUID
from typing import List

from app.application.exceptions import ResourceNotFoundError
from app.domain.entities.metric import TrainingMetric
from app.domain.repositories.metric_repository import TrainingMetricRepository


class TrainingMetricService:
    def __init__(self, repository: TrainingMetricRepository) -> None:
        self._repository = repository

    async def list_all(self) -> List[TrainingMetric]:
        return await self._repository.list()

    async def list_by_model(self, model_id: UUID) -> list[TrainingMetric]:
        return await self._repository.list_by_model(model_id)

    async def get(self, metric_id: UUID) -> TrainingMetric:
        metric = await self._repository.get_by_id(metric_id)
        if metric is None:
            raise ResourceNotFoundError("Metric not found")
        return metric

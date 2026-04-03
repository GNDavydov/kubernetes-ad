from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.metric import TrainingMetric


class TrainingMetricRepository(ABC):

    @abstractmethod
    async def add(self, metric: TrainingMetric) -> TrainingMetric:
        ...

    @abstractmethod
    async def list(self) -> List[TrainingMetric]:
        ...

    @abstractmethod
    async def list_by_model(self, model_id: UUID) -> List[TrainingMetric]:
        ...

    @abstractmethod
    async def get_by_id(self, metric_id: UUID) -> TrainingMetric | None:
        ...

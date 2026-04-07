from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.train_metric import TrainMetric


class TrainMetricRepository(ABC):

    @abstractmethod
    async def create(self, train_metric: TrainMetric) -> TrainMetric:
        ...

    @abstractmethod
    async def list(self) -> List[TrainMetric]:
        ...

    @abstractmethod
    async def list_by_task(self, task_id: UUID) -> List[TrainMetric]:
        ...

    @abstractmethod
    async def get_by_id(self, train_metric_id: UUID) -> TrainMetric | None:
        ...

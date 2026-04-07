from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from backend.app.domain.entities.detect_metric import DetectMetric


class DetectMetricRepository(ABC):

    @abstractmethod
    async def create(self, detect_metric: DetectMetric) -> DetectMetric:
        ...

    @abstractmethod
    async def list(self) -> List[DetectMetric]:
        ...

    @abstractmethod
    async def list_by_task(self, task_id: UUID) -> List[DetectMetric]:
        ...

    @abstractmethod
    async def get_by_id(self, detect_metric_id: UUID) -> DetectMetric | None:
        ...

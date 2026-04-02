from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.metric import TrainingMetric


class TrainingMetricRepository(ABC):

    @abstractmethod
    def add(self, metric: TrainingMetric) -> TrainingMetric:
        ...

    @abstractmethod
    def list(self) -> List[TrainingMetric]:
        ...

    @abstractmethod
    def list_by_model(self, model_id: int) -> List[TrainingMetric]:
        ...

    @abstractmethod
    def get_by_id(self, metric_id: int) -> TrainingMetric | None:
        ...

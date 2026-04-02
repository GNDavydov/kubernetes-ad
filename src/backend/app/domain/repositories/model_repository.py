from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.model import Model


class ModelRepository(ABC):

    @abstractmethod
    def add(self, model: Model) -> Model:
        ...

    @abstractmethod
    def list(self) -> List[Model]:
        ...

    @abstractmethod
    def get_by_id(self, model_id: int) -> Model | None:
        ...

    @abstractmethod
    def update(self, model: Model) -> Model:
        ...

    @abstractmethod
    def delete(self, model_id: int) -> None:
        ...

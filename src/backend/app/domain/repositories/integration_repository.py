from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.integration import Integration


class IntegrationRepository(ABC):

    @abstractmethod
    def add(self, integration: Integration) -> Integration:
        ...

    @abstractmethod
    def list(self) -> List[Integration]:
        ...

    @abstractmethod
    def get_by_id(self, integration_id: int) -> Integration | None:
        ...

    @abstractmethod
    def update(self, integration: Integration) -> Integration:
        ...

    @abstractmethod
    def delete(self, integration_id: int) -> None:
        ...

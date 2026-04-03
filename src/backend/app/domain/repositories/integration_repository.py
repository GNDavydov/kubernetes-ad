from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.integration import Integration


class IntegrationRepository(ABC):

    @abstractmethod
    async def add(self, integration: Integration) -> Integration:
        ...

    @abstractmethod
    async def list(self) -> List[Integration]:
        ...

    @abstractmethod
    async def get_by_id(self, integration_id: UUID) -> Integration | None:
        ...

    @abstractmethod
    async def update(self, integration: Integration) -> Integration:
        ...

    @abstractmethod
    async def delete(self, integration_id: UUID) -> None:
        ...

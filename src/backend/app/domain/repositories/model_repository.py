from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.enums.model_status import ModelStatus
from app.domain.entities.model import Model


class ModelRepository(ABC):

    @abstractmethod
    async def create(self, model: Model) -> Model:
        ...

    @abstractmethod
    async def list(self) -> List[Model]:
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> List[Model]:
        ...

    @abstractmethod
    async def get_by_id(self, model_id: UUID) -> Model | None:
        ...

    @abstractmethod
    async def update(self, model: Model) -> Model:
        ...

    @abstractmethod
    async def update_status(self, model_id: UUID, status: ModelStatus) -> Model | None:
        ...

    @abstractmethod
    async def delete(self, model_id: UUID) -> None:
        ...

from datetime import datetime, timezone
from typing import Any, List
from uuid import UUID, uuid4

from app.application.exceptions import ResourceNotFoundError
from app.domain.entities.model import Model
from app.domain.enums.model_status import ModelStatus
from app.domain.repositories.model_repository import ModelRepository


class ModelService:
    def __init__(self, repository: ModelRepository) -> None:
        self._repository = repository

    async def create(
        self,
        name: str,
        status: ModelStatus,
        input_dim: int,
        seq_len: int,
        threshold: float,
        model_path: str,
        last_processed_at: datetime,
    ) -> Model:
        entity = Model(
            id=uuid4(),
            name=name,
            status=status,
            input_dim=input_dim,
            seq_len=seq_len,
            threshold=threshold,
            model_path=model_path,
            last_processed_at=last_processed_at,
            created_at=datetime.now(timezone.utc),
        )
        return await self._repository.add(entity)

    async def list_all(self) -> List[Model]:
        return await self._repository.list()

    async def get(self, model_id: UUID) -> Model:
        model = await self._repository.get_by_id(model_id)
        if model is None:
            raise ResourceNotFoundError("Model not found")
        return model

    async def replace(
        self,
        model_id: UUID,
        name: str,
        status: ModelStatus,
        input_dim: int,
        seq_len: int,
        threshold: float,
        model_path: str,
        last_processed_at: datetime,
    ) -> Model:
        current = await self._repository.get_by_id(model_id)
        if current is None:
            raise ResourceNotFoundError("Model not found")

        entity = Model(
            id=model_id,
            name=name,
            status=status,
            input_dim=input_dim,
            seq_len=seq_len,
            threshold=threshold,
            model_path=model_path,
            last_processed_at=last_processed_at,
            created_at=current.created_at,
        )
        return await self._repository.update(entity)

    async def partial_update(self, model_id: UUID, patch: dict[str, Any]) -> Model:
        current = await self._repository.get_by_id(model_id)
        if current is None:
            raise ResourceNotFoundError("Model not found")

        entity = Model(
            id=model_id,
            name=patch.get("name", current.name),
            status=patch.get("status", current.status),
            input_dim=patch.get("input_dim", current.input_dim),
            seq_len=patch.get("seq_len", current.seq_len),
            threshold=patch.get("threshold", current.threshold),
            model_path=patch.get("model_path", current.model_path),
            last_processed_at=patch.get(
                "last_processed_at", current.last_processed_at),
            created_at=current.created_at,
        )

        try:
            return await self._repository.update(entity)
        except ValueError as exc:
            raise ResourceNotFoundError("Model not found") from exc

    async def delete(self, model_id: UUID) -> None:
        current = await self._repository.get_by_id(model_id)
        if current is None:
            raise ResourceNotFoundError("Model not found")
        await self._repository.delete(model_id)

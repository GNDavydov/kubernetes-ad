from datetime import datetime
from uuid import UUID

from app.application.exceptions import ResourceNotFoundError
from app.core.constants import DEFAULT_MODEL_SEQ_LEN, DEFAULT_MODEL_THRESHOLD
from app.domain.entities.model import Model
from app.domain.enums.model_status import ModelStatus
from app.domain.repositories.model_repository import ModelRepository


class ModelService:
    def __init__(self, model_repository: ModelRepository) -> None:
        self._model_repository = model_repository

    async def create(
        self,
        user_id: UUID,
        name: str,
        model_path: str,
    ) -> Model:
        model = Model(
            id=None,
            user_id=user_id,
            name=name,
            status=ModelStatus.CREATED,
            seq_len=DEFAULT_MODEL_SEQ_LEN,
            threshold=DEFAULT_MODEL_THRESHOLD,
            model_path=model_path,
            last_processed_at=None,
            created_at=None,
        )
        return await self._model_repository.create(model)

    async def list_my(self, user_id: UUID) -> list[Model]:
        return await self._model_repository.list_by_user(user_id)

    async def get_my_by_id(self, user_id: UUID, model_id: UUID) -> Model:
        model = await self._model_repository.get_by_id(model_id)
        if model is None or model.user_id != user_id:
            raise ResourceNotFoundError("Model not found")
        return model

    async def update_my(
        self,
        user_id: UUID,
        model_id: UUID,
        name: str | None = None,
        model_path: str | None = None,
    ) -> Model:
        existing_model = await self.get_my_by_id(user_id=user_id, model_id=model_id)
        if existing_model is None:
            raise ResourceNotFoundError("Model not found")

        updated_model = Model(
            id=existing_model.id,
            user_id=existing_model.user_id,
            name=name if name is not None else existing_model.name,
            status=existing_model.status,
            seq_len=existing_model.seq_len,
            threshold=existing_model.threshold,
            model_path=model_path if model_path is not None else existing_model.model_path,
            last_processed_at=existing_model.last_processed_at,
            created_at=existing_model.created_at,
        )
        updated = await self._model_repository.update(updated_model)
        if updated is None:
            raise ResourceNotFoundError("Model not found")
        return updated

    async def delete_my(self, user_id: UUID, model_id: UUID) -> None:
        _ = await self.get_my_by_id(user_id=user_id, model_id=model_id)
        await self._model_repository.delete(model_id)

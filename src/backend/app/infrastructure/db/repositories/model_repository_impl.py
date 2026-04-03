from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.model import Model
from app.domain.repositories.model_repository import ModelRepository
from app.infrastructure.db.models.model import ModelModel


class ModelRepositoryImpl(ModelRepository):

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, model: Model) -> Model:
        db_model = ModelModel(
            name=model.name,
            status=model.status,
            input_dim=model.input_dim,
            seq_len=model.seq_len,
            threshold=model.threshold,
            model_path=model.model_path,
            last_processed_at=model.last_processed_at,
            created_at=model.created_at,
        )
        self.db.add(db_model)
        await self.db.commit()
        await self.db.refresh(db_model)
        return self._to_entity(db_model)

    async def list(self) -> List[Model]:
        result = await self.db.execute(select(ModelModel))
        db_models = result.scalars().all()
        return [self._to_entity(db_model) for db_model in db_models]

    async def get_by_id(self, model_id: UUID) -> Model | None:
        db_model = await self.db.get(ModelModel, model_id)
        return self._to_entity(db_model) if db_model else None

    async def update(self, model: Model) -> Model:
        db_model = await self.db.get(ModelModel, model.id)
        if db_model is None:
            raise ValueError(f"Model with id={model.id} not found")

        db_model.name = model.name
        db_model.status = model.status
        db_model.input_dim = model.input_dim
        db_model.seq_len = model.seq_len
        db_model.threshold = model.threshold
        db_model.model_path = model.model_path
        db_model.last_processed_at = model.last_processed_at
        await self.db.commit()
        await self.db.refresh(db_model)
        return self._to_entity(db_model)

    async def delete(self, model_id: UUID) -> None:
        db_model = await self.db.get(ModelModel, model_id)
        if db_model:
            await self.db.delete(db_model)
            await self.db.commit()

    @staticmethod
    def _to_entity(db_model: ModelModel) -> Model:
        return Model(
            id=db_model.id,
            name=db_model.name,
            status=db_model.status,
            input_dim=db_model.input_dim or 0,
            seq_len=db_model.seq_len,
            threshold=db_model.threshold or 0.0,
            model_path=db_model.model_path or "",
            last_processed_at=db_model.last_processed_at or db_model.created_at,
            created_at=db_model.created_at,
        )

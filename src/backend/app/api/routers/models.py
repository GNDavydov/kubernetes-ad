from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_model_service
from app.api.schemas.model import (
    ModelCreateSchema,
    ModelPatchSchema,
    ModelPutSchema,
    ModelReadSchema,
)
from app.application.services.model_service import ModelService


router = APIRouter(prefix="/models", tags=["models"])


@router.post("", response_model=ModelReadSchema, status_code=status.HTTP_201_CREATED)
async def create_model(
    payload: ModelCreateSchema,
    service: ModelService = Depends(get_model_service),
) -> ModelReadSchema:
    created = await service.create(
        name=payload.name,
        status=payload.status,
        input_dim=payload.input_dim,
        seq_len=payload.seq_len,
        threshold=payload.threshold,
        model_path=payload.model_path,
        last_processed_at=payload.last_processed_at,
    )
    return ModelReadSchema.model_validate(created)


@router.get("", response_model=list[ModelReadSchema])
async def list_models(
    service: ModelService = Depends(get_model_service),
) -> list[ModelReadSchema]:
    models = await service.list_all()
    return [ModelReadSchema.model_validate(item) for item in models]


@router.get("/{model_id}", response_model=ModelReadSchema)
async def get_model(
    model_id: UUID,
    service: ModelService = Depends(get_model_service),
) -> ModelReadSchema:
    model = await service.get(model_id)
    return ModelReadSchema.model_validate(model)


@router.put("/{model_id}", response_model=ModelReadSchema)
async def put_model(
    model_id: UUID,
    payload: ModelPutSchema,
    service: ModelService = Depends(get_model_service),
) -> ModelReadSchema:
    updated = await service.replace(
        model_id=model_id,
        name=payload.name,
        status=payload.status,
        input_dim=payload.input_dim,
        seq_len=payload.seq_len,
        threshold=payload.threshold,
        model_path=payload.model_path,
        last_processed_at=payload.last_processed_at,
    )
    return ModelReadSchema.model_validate(updated)


@router.patch("/{model_id}", response_model=ModelReadSchema)
async def patch_model(
    model_id: UUID,
    payload: ModelPatchSchema,
    service: ModelService = Depends(get_model_service),
) -> ModelReadSchema:
    patch = payload.model_dump(exclude_unset=True)
    updated = await service.partial_update(model_id, patch)
    return ModelReadSchema.model_validate(updated)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: UUID,
    service: ModelService = Depends(get_model_service),
) -> None:
    await service.delete(model_id)

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_model_service
from app.api.schemas.model import CreateModelRequest, ModelResponse, UpdateModelRequest
from app.api.schemas.user import MessageResponse
from app.application.services.model_service import ModelService
from app.domain.entities.model import Model
from app.domain.entities.user import User

router = APIRouter(prefix="/models", tags=["models"])


def _to_response(model: Model) -> ModelResponse:
    return ModelResponse(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        status=model.status,
        seq_len=model.seq_len,
        threshold=model.threshold,
        model_path=model.model_path,
        last_processed_at=model.last_processed_at,
        created_at=model.created_at,
    )


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    request: CreateModelRequest,
    current_user: User = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    model = await model_service.create(
        user_id=current_user.id,
        name=request.name,
        model_path=request.model_path,
    )
    return _to_response(model)


@router.get("", response_model=list[ModelResponse])
async def list_models(
    current_user: User = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> list[ModelResponse]:
    models = await model_service.list_my(user_id=current_user.id)
    return [_to_response(model) for model in models]


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model_by_id(
    model_id: UUID,
    current_user: User = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    model = await model_service.get_my_by_id(
        user_id=current_user.id,
        model_id=model_id,
    )
    return _to_response(model)


@router.delete("/{model_id}", response_model=MessageResponse)
async def delete_model(
    model_id: UUID,
    current_user: User = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> MessageResponse:
    await model_service.delete_my(
        user_id=current_user.id,
        model_id=model_id,
    )
    return MessageResponse(detail="Model deleted successfully")

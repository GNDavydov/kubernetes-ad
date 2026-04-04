from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_training_metric_service
from app.api.schemas.training_metric import TrainingMetricReadSchema
from app.application.services.metric_service import TrainingMetricService


router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=list[TrainingMetricReadSchema])
async def list_metrics(
    service: TrainingMetricService = Depends(get_training_metric_service),
    model_id: UUID | None = Query(default=None),
) -> list[TrainingMetricReadSchema]:
    if model_id is not None:
        metrics = await service.list_by_model(model_id)
    else:
        metrics = await service.list_all()
    return [TrainingMetricReadSchema.model_validate(m) for m in metrics]


@router.get("/{metric_id}", response_model=TrainingMetricReadSchema)
async def get_metric(
    metric_id: UUID,
    service: TrainingMetricService = Depends(get_training_metric_service),
) -> TrainingMetricReadSchema:
    metric = await service.get(metric_id)
    return TrainingMetricReadSchema.model_validate(metric)

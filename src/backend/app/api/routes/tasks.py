from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_task_service
from app.api.schemas.task import (
    CreateTaskRequest,
    DetectMetricResponse,
    TaskResponse,
    TrainMetricResponse,
)
from app.application.services.task_service import TaskService
from app.domain.entities.detect_metric import DetectMetric
from app.domain.entities.task import Task
from app.domain.entities.train_metric import TrainMetric
from app.domain.entities.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        model_id=task.model_id,
        integration_id=task.integration_id,
        user_id=task.user_id,
        type=task.type,
        status=task.status,
        epochs=task.epochs,
        created_at=task.created_at,
    )


def _to_train_metric_response(metric: TrainMetric) -> TrainMetricResponse:
    return TrainMetricResponse(
        id=metric.id,
        task_id=metric.task_id,
        processed_events=metric.processed_events,
        epoch=metric.epoch,
        loss=metric.loss,
        val_loss=metric.val_loss,
        duration=metric.duration,
        created_at=metric.created_at,
    )


def _to_detect_metric_response(metric: DetectMetric) -> DetectMetricResponse:
    return DetectMetricResponse(
        id=metric.id,
        task_id=metric.task_id,
        processed_events=metric.processed_events,
        anomalies_count=metric.anomalies_count,
        duration=metric.duration,
        created_at=metric.created_at,
        start_timestamp=metric.start_timestamp,
        end_timestamp=metric.end_timestamp,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await task_service.create(
        user_id=current_user.id,
        model_id=request.model_id,
        integration_id=request.integration_id,
        type=request.type,
        epochs=request.epochs,
    )
    return _to_response(task)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    tasks = await task_service.list_my(user_id=current_user.id)
    return [_to_response(task) for task in tasks]


@router.get("/{task_id}/train-metrics", response_model=list[TrainMetricResponse])
async def list_task_train_metrics(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> list[TrainMetricResponse]:
    metrics = await task_service.list_my_train_metrics(
        user_id=current_user.id,
        task_id=task_id,
    )
    return [_to_train_metric_response(metric) for metric in metrics]


@router.get("/{task_id}/detect-metrics", response_model=list[DetectMetricResponse])
async def list_task_detect_metrics(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> list[DetectMetricResponse]:
    metrics = await task_service.list_my_detect_metrics(
        user_id=current_user.id,
        task_id=task_id,
    )
    return [_to_detect_metric_response(metric) for metric in metrics]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await task_service.get_my_by_id(
        user_id=current_user.id,
        task_id=task_id,
    )
    return _to_response(task)


router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        model_id=task.model_id,
        integration_id=task.integration_id,
        user_id=task.user_id,
        type=task.type,
        status=task.status,
        epochs=task.epochs,
        created_at=task.created_at,
    )


def _to_train_metric_response(metric: TrainMetric) -> TrainMetricResponse:
    return TrainMetricResponse(
        id=metric.id,
        task_id=metric.task_id,
        processed_events=metric.processed_events,
        epoch=metric.epoch,
        loss=metric.loss,
        val_loss=metric.val_loss,
        duration=metric.duration,
        created_at=metric.created_at,
    )


def _to_detect_metric_response(metric: DetectMetric) -> DetectMetricResponse:
    return DetectMetricResponse(
        id=metric.id,
        task_id=metric.task_id,
        processed_events=metric.processed_events,
        anomalies_count=metric.anomalies_count,
        duration=metric.duration,
        created_at=metric.created_at,
        start_timestamp=metric.start_timestamp,
        end_timestamp=metric.end_timestamp,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await task_service.create(
        user_id=current_user.id,
        model_id=request.model_id,
        integration_id=request.integration_id,
        type=request.type,
        epochs=request.epochs,
    )
    return _to_response(task)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    tasks = await task_service.list_my(user_id=current_user.id)
    return [_to_response(task) for task in tasks]


@router.get("/{task_id}/train-metrics", response_model=list[TrainMetricResponse])
async def list_task_train_metrics(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> list[TrainMetricResponse]:
    metrics = await task_service.list_my_train_metrics(
        user_id=current_user.id,
        task_id=task_id,
    )
    return [_to_train_metric_response(metric) for metric in metrics]


@router.get("/{task_id}/detect-metrics", response_model=list[DetectMetricResponse])
async def list_task_detect_metrics(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> list[DetectMetricResponse]:
    metrics = await task_service.list_my_detect_metrics(
        user_id=current_user.id,
        task_id=task_id,
    )
    return [_to_detect_metric_response(metric) for metric in metrics]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await task_service.get_my_by_id(
        user_id=current_user.id,
        task_id=task_id,
    )
    return _to_response(task)

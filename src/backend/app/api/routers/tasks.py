from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_task_service
from app.api.schemas.task import TaskReadSchema
from app.application.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskReadSchema])
async def list_tasks(
    service: TaskService = Depends(get_task_service),
    model_id: UUID | None = Query(default=None),
    integration_id: UUID | None = Query(default=None),
) -> list[TaskReadSchema]:
    if model_id is not None:
        tasks = await service.list_by_model(model_id)
    elif integration_id is not None:
        tasks = await service.list_by_integration(integration_id)
    else:
        tasks = await service.list_all()
    return [TaskReadSchema.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskReadSchema)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskReadSchema:
    task = await service.get(task_id)
    return TaskReadSchema.model_validate(task)

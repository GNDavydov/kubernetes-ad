from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_task_result_service
from app.api.schemas.task_result import TaskResultReadSchema
from app.application.services.task_result_service import TaskResultService


router = APIRouter(prefix="/task-results", tags=["task-results"])


@router.get("", response_model=list[TaskResultReadSchema])
async def list_task_results(
    service: TaskResultService = Depends(get_task_result_service),
) -> list[TaskResultReadSchema]:
    results = await service.list_all()
    return [TaskResultReadSchema.model_validate(r) for r in results]


@router.get("/by-task/{task_id}", response_model=TaskResultReadSchema)
async def get_task_result_by_task(
    task_id: UUID,
    service: TaskResultService = Depends(get_task_result_service),
) -> TaskResultReadSchema:
    result = await service.get_by_task(task_id)
    return TaskResultReadSchema.model_validate(result)


@router.get("/{task_result_id}", response_model=TaskResultReadSchema)
async def get_task_result(
    task_result_id: UUID,
    service: TaskResultService = Depends(get_task_result_service),
) -> TaskResultReadSchema:
    result = await service.get(task_result_id)
    return TaskResultReadSchema.model_validate(result)

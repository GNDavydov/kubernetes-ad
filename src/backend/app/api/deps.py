from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.integration_service import IntegrationService
from app.application.services.metric_service import TrainingMetricService
from app.application.services.model_service import ModelService
from app.application.services.task_result_service import TaskResultService
from app.application.services.task_service import TaskService
from app.domain.repositories.integration_repository import IntegrationRepository
from app.domain.repositories.metric_repository import TrainingMetricRepository
from app.domain.repositories.model_repository import ModelRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.task_result_repository import TaskResultRepository
from app.infrastructure.db.database import Database
from app.infrastructure.db.repositories.integration_repository_impl import IntegrationRepositoryImpl
from app.infrastructure.db.repositories.metric_repository_impl import TrainingMetricRepositoryImpl
from app.infrastructure.db.repositories.model_repository_impl import ModelRepositoryImpl
from app.infrastructure.db.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.db.repositories.task_result_repository_impl import TaskResultRepositoryImpl


def get_database(request: Request) -> Database:
    return request.app.state.database


async def get_db_session(
    database: Database = Depends(get_database),
) -> AsyncIterator[AsyncSession]:
    async for session in database.get_db():
        yield session


def get_integration_repository(
    db: AsyncSession = Depends(get_db_session),
) -> IntegrationRepository:
    return IntegrationRepositoryImpl(db)


def get_model_repository(
    db: AsyncSession = Depends(get_db_session),
) -> ModelRepository:
    return ModelRepositoryImpl(db)


def get_task_repository(
    db: AsyncSession = Depends(get_db_session),
) -> TaskRepository:
    return TaskRepositoryImpl(db)


def get_training_metric_repository(
    db: AsyncSession = Depends(get_db_session),
) -> TrainingMetricRepository:
    return TrainingMetricRepositoryImpl(db)


def get_task_result_repository(
    db: AsyncSession = Depends(get_db_session),
) -> TaskResultRepository:
    return TaskResultRepositoryImpl(db)


def get_integration_service(
    repository: IntegrationRepository = Depends(get_integration_repository),
) -> IntegrationService:
    return IntegrationService(repository)


def get_model_service(
    repository: ModelRepository = Depends(get_model_repository),
) -> ModelService:
    return ModelService(repository)


def get_task_service(
    repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(repository)


def get_training_metric_service(
    repository: TrainingMetricRepository = Depends(get_training_metric_repository),
) -> TrainingMetricService:
    return TrainingMetricService(repository)


def get_task_result_service(
    repository: TaskResultRepository = Depends(get_task_result_repository),
) -> TaskResultService:
    return TaskResultService(repository)

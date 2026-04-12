from fastapi import Depends

from app.api.dependencies.common import (
    get_detect_metric_repository,
    get_integration_repository,
    get_model_repository,
    get_task_repository,
    get_train_metric_repository,
    get_user_repository,
)
from app.api.dependencies.auth import get_password_hasher
from app.application.services.integration_service import IntegrationService
from app.application.services.model_service import ModelService
from app.application.services.task_service import TaskService
from app.application.services.user_service import UserService
from app.domain.repositories.detect_metric_repository import DetectMetricRepository
from app.domain.repositories.integration_repository import IntegrationRepository
from app.domain.repositories.model_repository import ModelRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.train_metric_repository import TrainMetricRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.interfaces.password_hasher import PasswordHasher


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher)
) -> UserService:
    return UserService(
        user_repository=user_repository,
        password_hasher=password_hasher
    )


def get_model_service(
    model_repository: ModelRepository = Depends(get_model_repository),
) -> ModelService:
    return ModelService(model_repository=model_repository)


def get_integration_service(
    integration_repository: IntegrationRepository = Depends(
        get_integration_repository),
) -> IntegrationService:
    return IntegrationService(integration_repository=integration_repository)


def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
    model_repository: ModelRepository = Depends(get_model_repository),
    integration_repository: IntegrationRepository = Depends(
        get_integration_repository),
    train_metric_repository: TrainMetricRepository = Depends(
        get_train_metric_repository),
    detect_metric_repository: DetectMetricRepository = Depends(
        get_detect_metric_repository),
) -> TaskService:
    return TaskService(
        task_repository=task_repository,
        model_repository=model_repository,
        integration_repository=integration_repository,
        train_metric_repository=train_metric_repository,
        detect_metric_repository=detect_metric_repository,
    )

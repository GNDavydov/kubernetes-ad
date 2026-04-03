from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.integration_service import IntegrationService
from app.application.services.model_service import ModelService
from app.domain.repositories.integration_repository import IntegrationRepository
from app.domain.repositories.model_repository import ModelRepository
from app.infrastructure.db.database import Database
from app.infrastructure.db.repositories.integration_repository_impl import IntegrationRepositoryImpl
from app.infrastructure.db.repositories.model_repository_impl import ModelRepositoryImpl


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


def get_integration_service(
    repository: IntegrationRepository = Depends(get_integration_repository),
) -> IntegrationService:
    return IntegrationService(repository)


def get_model_service(
    repository: ModelRepository = Depends(get_model_repository),
) -> ModelService:
    return ModelService(repository)

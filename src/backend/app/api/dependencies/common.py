from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.integration_repository import IntegrationRepository
from app.domain.repositories.model_repository import ModelRepository
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.db.database import Database
from app.infrastructure.db.repositories.integration_repository_impl import IntegrationRepositoryImpl
from app.infrastructure.db.repositories.model_repository_impl import ModelRepositoryImpl
from app.infrastructure.db.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl


def get_database(request: Request) -> Database:
    return request.app.state.database


async def get_db_session(
    database: Database = Depends(get_database),
) -> AsyncIterator[AsyncSession]:
    async for session in database.get_db():
        yield session


def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepositoryImpl(db)


def get_model_repository(
    db: AsyncSession = Depends(get_db_session),
) -> ModelRepository:
    return ModelRepositoryImpl(db)


def get_integration_repository(
    db: AsyncSession = Depends(get_db_session),
) -> IntegrationRepository:
    return IntegrationRepositoryImpl(db)


def get_task_repository(
    db: AsyncSession = Depends(get_db_session),
) -> TaskRepository:
    return TaskRepositoryImpl(db)

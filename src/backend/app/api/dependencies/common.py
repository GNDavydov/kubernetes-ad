from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.db.database import Database
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



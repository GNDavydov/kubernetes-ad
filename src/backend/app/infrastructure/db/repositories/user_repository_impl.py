from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.enums.role import Role
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.db.models.user import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user: User) -> User:
        db_user = UserModel(
            email=user.email,
            password=user.password,
            role=user.role,
            created_at=user.created_at or datetime.now(timezone.utc),
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return self._to_entity(db_user)

    async def list(self) -> List[User]:
        result = await self.db.execute(select(UserModel))
        db_users = result.scalars().all()
        return [self._to_entity(db_user) for db_user in db_users]

    async def get_by_id(self, user_id: UUID) -> User | None:
        db_user = await self.db.get(UserModel, user_id)
        return self._to_entity(db_user) if db_user else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(UserModel).where(UserModel.email == email))
        db_user = result.scalars().first()
        return self._to_entity(db_user) if db_user else None

    async def update(self, user: User) -> User:
        if user.id is None:
            raise ValueError("User id is required for update")
        db_user = await self.db.get(UserModel, user.id)
        if db_user is None:
            raise ValueError(f"User with id={user.id} not found")

        db_user.email = user.email
        db_user.password = user.password
        db_user.role = user.role
        await self.db.commit()
        await self.db.refresh(db_user)
        return self._to_entity(db_user)

    async def update_password(self, user_id: UUID, password: str) -> User | None:
        db_user = await self.db.get(UserModel, user_id)
        if db_user is None:
            return None
        db_user.password = password
        await self.db.commit()
        await self.db.refresh(db_user)
        return self._to_entity(db_user)

    async def update_email(self, user_id: UUID, email: str) -> User | None:
        db_user = await self.db.get(UserModel, user_id)
        if db_user is None:
            return None
        db_user.email = email
        await self.db.commit()
        await self.db.refresh(db_user)
        return self._to_entity(db_user)

    async def update_role(self, user_id: UUID, role: Role) -> User | None:
        db_user = await self.db.get(UserModel, user_id)
        if db_user is None:
            return None
        db_user.role = role
        await self.db.commit()
        await self.db.refresh(db_user)
        return self._to_entity(db_user)

    async def delete(self, user_id: UUID) -> None:
        db_user = await self.db.get(UserModel, user_id)
        if db_user:
            await self.db.delete(db_user)
            await self.db.commit()

    @staticmethod
    def _to_entity(db_user: UserModel) -> User:
        return User(
            id=db_user.id,
            email=db_user.email,
            password=db_user.password,
            role=db_user.role,
            created_at=db_user.created_at,
        )

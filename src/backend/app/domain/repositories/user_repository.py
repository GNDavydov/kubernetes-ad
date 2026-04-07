from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums.role import Role


class UserRepository(ABC):

    @abstractmethod
    async def create(self, user: User) -> User:
        ...

    @abstractmethod
    async def list(self) -> List[User]:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...

    @abstractmethod
    async def update_password(self, user_id: UUID, password: str) -> User | None:
        ...

    @abstractmethod
    async def update_email(self, user_id: UUID, email: str) -> User | None:
        ...

    @abstractmethod
    async def update_role(self, user_id: UUID, role: Role) -> User | None:
        ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        ...

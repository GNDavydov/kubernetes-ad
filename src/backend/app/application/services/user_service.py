from uuid import UUID

from app.application.exceptions import (
    AuthenticationError,
    ConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from app.domain.entities.user import User
from app.domain.enums.role import Role
from app.domain.interfaces.password_hasher import PasswordHasher
from app.domain.repositories.user_repository import UserRepository


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def create(
        self,
        email: str,
        password: str,
        role: Role,
    ) -> User:
        if not email.strip():
            raise ValidationError("Email must not be empty")

        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long")

        existing_user = await self._user_repository.get_by_email(email)
        if existing_user is not None:
            raise ConflictError("User with this email already exists")

        password_hash = self._password_hasher.hash_password(password)
        user = User(
            id=None,
            email=email,
            password=password_hash,
            role=role,
            created_at=None,
        )
        return await self._user_repository.create(user)

    async def list_users(self) -> list[User]:
        return await self._user_repository.list()

    async def get_user_by_id(self, user_id: UUID) -> User:
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundError("User not found")
        return user

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundError("User not found")

        is_current_password_valid = self._password_hasher.verify_password(
            current_password,
            user.password,
        )
        if not is_current_password_valid:
            raise AuthenticationError("Current password is invalid")

        if len(new_password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long")

        is_same_password = self._password_hasher.verify_password(
            new_password,
            user.password,
        )
        if is_same_password:
            raise ValidationError(
                "New password must be different from current password")

        new_password_hash = self._password_hasher.hash_password(new_password)
        updated_user = await self._user_repository.update_password(
            user_id=user_id,
            password=new_password_hash,
        )
        if updated_user is None:
            raise ResourceNotFoundError("User not found")

    async def admin_set_password(
        self,
        user_id: UUID,
        new_password: str,
    ) -> None:
        if len(new_password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long")

        new_password_hash = self._password_hasher.hash_password(new_password)
        updated_user = await self._user_repository.update_password(
            user_id=user_id,
            password=new_password_hash,
        )
        if updated_user is None:
            raise ResourceNotFoundError("User not found")

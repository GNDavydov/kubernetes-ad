from fastapi import Depends

from app.api.dependencies.common import get_user_repository
from app.api.dependencies.auth import get_password_hasher
from app.application.services.user_service import UserService
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

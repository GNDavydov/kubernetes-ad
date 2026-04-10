from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.common import get_user_repository
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.domain.entities.user import User
from app.domain.enums.role import Role
from app.domain.repositories.user_repository import UserRepository
from app.domain.interfaces.token_service import TokenService
from app.domain.interfaces.password_hasher import PasswordHasher


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hasher(request: Request) -> PasswordHasher:
    return request.app.state.password_hasher


def get_token_service(request: Request) -> TokenService:
    return request.app.state.token_service


def get_authenticate_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_service=token_service,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:
        payload = token_service.decode_access_token(token)
    except Exception as exc:
        raise unauthorized_exception from exc

    subject = payload.sub
    if not subject:
        raise unauthorized_exception

    try:
        user_id = UUID(subject)
    except ValueError as exc:
        raise unauthorized_exception from exc

    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise unauthorized_exception

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role is required",
        )
    return current_user

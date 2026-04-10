from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.common import get_user_repository
from app.application.exceptions import AuthenticationError, AuthorizationError
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.domain.entities.access_token_payload import AccessTokenPayload
from app.domain.entities.user import User
from app.domain.enums.role import Role
from app.domain.interfaces.token_blacklist import TokenBlacklist
from app.domain.interfaces.token_service import TokenService
from app.domain.interfaces.password_hasher import PasswordHasher
from app.domain.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hasher(request: Request) -> PasswordHasher:
    return request.app.state.password_hasher


def get_token_service(request: Request) -> TokenService:
    return request.app.state.token_service


def get_token_blacklist(request: Request) -> TokenBlacklist:
    return request.app.state.token_blacklist


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


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
    token_service: TokenService = Depends(get_token_service),
    token_blacklist: TokenBlacklist = Depends(get_token_blacklist),
) -> AccessTokenPayload:
    unauthorized_exception = AuthenticationError(
        "Could not validate credentials")

    try:
        payload = token_service.decode_access_token(token)
    except Exception as exc:
        raise unauthorized_exception from exc

    is_revoked = await token_blacklist.is_revoked(payload.jti)
    if is_revoked:
        raise unauthorized_exception

    return payload


async def get_current_user(
    payload: AccessTokenPayload = Depends(get_current_token_payload),
) -> User:
    return User(
        id=payload.user_id,
        email=payload.email,
        password="",
        role=payload.role,
        created_at=payload.created_at,
    )


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise AuthorizationError("Admin role is required")
    return current_user

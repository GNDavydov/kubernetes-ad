from app.application.exceptions import AuthenticationError
from app.domain.interfaces.password_hasher import PasswordHasher
from app.domain.interfaces.token_service import TokenService
from app.domain.repositories.user_repository import UserRepository


class AuthenticateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def execute(self, email: str, password: str) -> str:
        user = await self._user_repository.get_by_email(email)
        if user is None:
            raise AuthenticationError("Invalid email or password")

        is_password_valid = self._password_hasher.verify_password(
            password, user.password)
        if not is_password_valid:
            raise AuthenticationError("Invalid email or password")

        return self._token_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )

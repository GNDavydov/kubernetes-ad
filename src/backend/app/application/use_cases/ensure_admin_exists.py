from app.domain.entities.user import User
from app.domain.enums.role import Role
from app.domain.interfaces.password_hasher import PasswordHasher
from app.domain.repositories.user_repository import UserRepository


class EnsureAdminExistsUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, admin_email: str, admin_password: str) -> None:
        if not admin_email.strip() or not admin_password:
            return

        users = await self._user_repository.list()
        has_admin = any(user.role == Role.ADMIN for user in users)
        if has_admin:
            return

        existing_admin = await self._user_repository.get_by_email(admin_email)
        if existing_admin is not None:
            return

        password_hash = self._password_hasher.hash_password(admin_password)
        admin_user = User(
            id=None,
            email=admin_email,
            password=password_hash,
            role=Role.ADMIN,
            created_at=None,
        )
        await self._user_repository.create(admin_user)

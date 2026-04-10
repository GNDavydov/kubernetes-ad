from typing import Protocol
from datetime import datetime
from uuid import UUID

from app.domain.entities.access_token_payload import AccessTokenPayload
from app.domain.enums.role import Role


class TokenService(Protocol):
    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        role: Role,
        created_at: datetime | None,
    ) -> str:
        ...

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        ...

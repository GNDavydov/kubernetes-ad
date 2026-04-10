from typing import Protocol

from app.domain.entities.access_token_payload import AccessTokenPayload
from app.domain.enums.role import Role


class TokenService(Protocol):
    def create_access_token(self, subject: str, role: Role) -> str:
        ...

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        ...

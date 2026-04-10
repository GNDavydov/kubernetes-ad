from datetime import datetime, timedelta, timezone

import jwt

from app.domain.entities.access_token_payload import AccessTokenPayload
from app.domain.enums.role import Role
from app.domain.interfaces.token_service import TokenService


class JwtTokenService(TokenService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(self, subject: str, role: Role) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )
        payload = {
            "sub": subject,
            "role": role.value,
            "exp": expires_at,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        payload = jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
        )
        return AccessTokenPayload(
            sub=str(payload["sub"]),
            role=Role(payload["role"]),
            exp=payload["exp"],
        )

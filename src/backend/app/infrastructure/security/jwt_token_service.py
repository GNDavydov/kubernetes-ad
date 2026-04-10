from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

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

    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        role: Role,
        created_at: datetime | None,
    ) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )
        jti = str(uuid4())
        payload = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "email": email,
            "role": role.value,
            "created_at": created_at.isoformat() if created_at else None,
            "jti": jti,
            "exp": expires_at,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        payload = jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
        )
        user_id_raw = payload["user_id"]
        email = payload["email"]
        role_raw = payload["role"]
        created_at_raw = payload.get("created_at")
        jti = payload["jti"]
        exp = int(payload["exp"])

        created_at = None
        if created_at_raw:
            created_at = datetime.fromisoformat(created_at_raw)

        return AccessTokenPayload(
            user_id=UUID(str(user_id_raw)),
            email=str(email),
            role=Role(role_raw),
            created_at=created_at,
            jti=str(jti),
            exp=exp,
        )

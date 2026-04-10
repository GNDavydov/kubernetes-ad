from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.role import Role


@dataclass
class AccessTokenPayload:
    user_id: UUID
    email: str
    role: Role
    created_at: datetime | None
    jti: str
    exp: int

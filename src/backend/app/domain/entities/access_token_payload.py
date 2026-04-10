from dataclasses import dataclass
from datetime import datetime

from app.domain.enums.role import Role


@dataclass
class AccessTokenPayload:
    sub: str
    role: Role
    exp: datetime | int

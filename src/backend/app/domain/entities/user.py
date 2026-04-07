from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.role import Role


@dataclass
class User:
    id: UUID | None
    email: UUID
    password: str
    role: Role
    created_at: datetime | None

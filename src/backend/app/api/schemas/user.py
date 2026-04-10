from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.role import Role


class CreateUserRequest(BaseModel):
    email: str
    password: str
    role: Role = Role.USER


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: Role
    created_at: datetime | None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AdminSetPasswordRequest(BaseModel):
    new_password: str


class MessageResponse(BaseModel):
    detail: str

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateIntegrationRequest(BaseModel):
    name: str
    url: str
    username: str | None = None
    password: str | None = None
    index_name: str


class UpdateIntegrationRequest(BaseModel):
    name: str | None = None
    url: str | None = None
    username: str | None = None
    password: str | None = None
    index_name: str | None = None


class IntegrationResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    url: str
    username: str | None
    index_name: str
    created_at: datetime | None

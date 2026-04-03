from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IntegrationCreateSchema(BaseModel):
    name: str
    url: str
    username: str
    password: str
    index_name: str


class IntegrationPutSchema(BaseModel):
    name: str
    url: str
    username: str
    password: str
    index_name: str


class IntegrationPatchSchema(BaseModel):
    name: str | None = None
    url: str | None = None
    username: str | None = None
    password: str | None = None
    index_name: str | None = None


class IntegrationReadSchema(BaseModel):
    id: UUID
    name: str
    url: str
    username: str
    index_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.model_status import ModelStatus


class CreateModelRequest(BaseModel):
    name: str
    model_path: str


class UpdateModelRequest(BaseModel):
    name: str | None = None
    status: ModelStatus | None = None
    seq_len: int | None = None
    threshold: float | None = None
    model_path: str | None = None
    last_processed_at: datetime | None = None


class ModelResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    status: ModelStatus
    seq_len: int
    threshold: float
    model_path: str
    last_processed_at: datetime | None
    created_at: datetime | None

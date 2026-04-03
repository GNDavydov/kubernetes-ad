from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums.model_status import ModelStatus


class ModelCreateSchema(BaseModel):
    name: str
    status: ModelStatus
    input_dim: int
    seq_len: int
    threshold: float
    model_path: str
    last_processed_at: datetime


class ModelPutSchema(BaseModel):
    name: str
    status: ModelStatus
    input_dim: int
    seq_len: int
    threshold: float
    model_path: str
    last_processed_at: datetime


class ModelPatchSchema(BaseModel):
    name: str | None = None
    status: ModelStatus | None = None
    input_dim: int | None = None
    seq_len: int | None = None
    threshold: float | None = None
    model_path: str | None = None
    last_processed_at: datetime | None = None


class ModelReadSchema(BaseModel):
    id: UUID
    name: str
    status: ModelStatus
    input_dim: int
    seq_len: int
    threshold: float
    model_path: str
    last_processed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

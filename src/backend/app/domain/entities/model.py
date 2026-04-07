from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.model_status import ModelStatus


@dataclass
class Model:
    id: UUID | None
    user_id: UUID
    name: str
    status: ModelStatus
    seq_len: int
    threshold: float
    model_path: str
    last_processed_at: datetime | None
    created_at: datetime | None

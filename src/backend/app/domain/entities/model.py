from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.model_status import ModelStatus


@dataclass
class Model:
    id: UUID
    name: str
    status: ModelStatus
    input_dim: int
    seq_len: int
    threshold: float
    model_path: str
    last_processed_at: datetime
    created_at: datetime

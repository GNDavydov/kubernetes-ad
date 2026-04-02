from dataclasses import dataclass
from datetime import datetime


@dataclass
class Model:
    id: int
    name: str
    status: str
    input_dim: int
    threshold: float
    last_processed_at: datetime
    created_at: datetime

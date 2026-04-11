from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Integration:
    id: UUID | None
    user_id: UUID
    name: str
    url: str
    username: str | None
    password: str | None
    log_source_name: str
    anomaly_name: str
    created_at: datetime | None

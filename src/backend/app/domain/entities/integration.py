from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Integration:
    id: UUID | None
    name: str
    url: str
    username: str | None
    password: str | None
    index_name: str
    created_at: datetime

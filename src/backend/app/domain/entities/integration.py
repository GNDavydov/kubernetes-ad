from dataclasses import dataclass
from datetime import datetime


@dataclass
class Integration:
    id: int
    name: str
    url: str
    username: str | None
    password: str | None
    index_name: str
    created_at: datetime

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SequenceWindowDescriptor:
    user_username: str
    start_timestamp: datetime
    end_timestamp: datetime

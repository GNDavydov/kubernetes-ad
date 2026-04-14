from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class AuditEvent:
    timestamp: datetime
    verb: str
    user_username: str
    user_agent: str
    object_resource: str
    object_subresource: Optional[str]
    object_namespace: Optional[str]
    response_code: Optional[int]
    source_ips: list[str]

    def timestamp_as_datetime(self) -> datetime:
        if self.timestamp.tzinfo is None:
            return self.timestamp.replace(tzinfo=timezone.utc)
        return self.timestamp

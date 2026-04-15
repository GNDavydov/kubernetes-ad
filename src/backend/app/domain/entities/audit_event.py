from datetime import datetime, timezone
from typing import Any, Optional


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

    def __init__(self,
                 timestamp: datetime,
                 verb: str,
                 user_username: str,
                 user_agent: str,
                 object_resource: str,
                 object_subresource: Optional[str],
                 object_namespace: Optional[str],
                 response_code: Optional[int],
                 source_ips: list[str]
                 ) -> None:
        self.timestamp = timestamp
        self.verb = verb
        self.user_username = user_username
        self.user_agent = user_agent
        self.object_resource = object_resource
        self.object_subresource = object_subresource
        self.object_namespace = object_namespace
        self.response_code = response_code
        self.source_ips = source_ips
        self.vec = None

    def timestamp_as_datetime(self) -> datetime:
        if self.timestamp.tzinfo is None:
            return self.timestamp.replace(tzinfo=timezone.utc)
        return self.timestamp

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuditEvent:
    timestamp: str
    verb: str
    user_username: str
    user_agent: str
    object_resource: str
    object_subresource: Optional[str]
    object_namespace: Optional[str]
    response_code: Optional[int]
    source_ips: list[str]

    def timestamp_as_datetime(self) -> Optional[datetime]:
        """Преобразует timestamp в объект даты/времени.

        Returns:
            `datetime`, если строка корректна, иначе `None`.
        """
        try:
            normalized = self.timestamp.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except Exception:
            return None

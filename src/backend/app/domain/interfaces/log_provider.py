from datetime import datetime
from typing import Any, Optional, Protocol

from app.domain.entities.audit_event import AuditEvent


class LogProvider(Protocol):
    def fetch_audit_events(
        self,
        start_ts: Optional[datetime] = None,
        end_ts: Optional[datetime] = None,
        size: Optional[int] = None,
    ) -> list[AuditEvent]:
        ...

    def save_anomalies(self, documents: list[dict[str, Any]]) -> None:
        ...

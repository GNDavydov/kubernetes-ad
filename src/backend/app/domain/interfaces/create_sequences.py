from typing import Protocol, List

from app.domain.entities.audit_event import AuditEvent


class CreateSequences(Protocol):
    def transform(self, events: List[AuditEvent]) -> List[list]:
        ...

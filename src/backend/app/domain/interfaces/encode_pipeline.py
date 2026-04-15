from typing import Protocol, List

from app.domain.entities.audit_event import AuditEvent


class EncodePipeline(Protocol):
    def transform(self, event: AuditEvent) -> List:
        ...

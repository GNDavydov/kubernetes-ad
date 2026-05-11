from typing import Protocol

from app.domain.entities.audit_event import AuditEvent


class EncodePipeline(Protocol):
    def transform(self, event: AuditEvent) -> None:
        ...

    def shape(self) -> int:
        ...

from typing import Protocol, List

from app.domain.entities.audit_event import AuditEvent


class EncodePipeline(Protocol):
    def fit(self) -> None:
        ...

    def transform(self, event: AuditEvent) -> List:
        ...

from typing import Protocol, List, Tuple

from app.domain.entities.audit_event import AuditEvent


class CreateSequences(Protocol):
    def transform(self, events: List[AuditEvent]) -> List[list]:
        ...

    def shape(self) -> Tuple[int, int]:
        ...

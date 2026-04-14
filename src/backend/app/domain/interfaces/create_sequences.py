from typing import Protocol, List

from app.domain.entities.audit_event import AuditEvent
from app.domain.entities.audit_dataset import AuditDataset


class CreateSequences(Protocol):
    def transform(self, events: List[AuditEvent]) -> List[AuditDataset]:
        ...

from dataclasses import dataclass, field
from typing import Iterable, List

from app.domain.entities.audit_event import AuditEvent


@dataclass
class AuditDataset:
    events: List[AuditEvent] = field(default_factory=list)

    def add(self, event: AuditEvent) -> None:
        self.events.append(event)

    def __len__(self) -> int:
        return len(self.events)

    def __getitem__(self, idx: int) -> AuditEvent:
        return self.events[idx]

    def __iter__(self) -> Iterable[AuditEvent]:
        return iter(self.events)

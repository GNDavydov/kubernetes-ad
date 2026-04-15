from collections import defaultdict
from typing import List

from app.domain.entities.audit_event import AuditEvent
from app.domain.interfaces.create_sequences import CreateSequences
from app.domain.interfaces.encode_pipeline import EncodePipeline


class CreateSequencesImpl(CreateSequences):
    def __init__(self, encode_pipeline: EncodePipeline, seq_len: int) -> None:
        self.encode_pipeline = encode_pipeline
        self.seq_len = seq_len

    def transform(self, events: list[AuditEvent]) -> list[list]:
        grouped: dict[str, List[AuditEvent]] = defaultdict(list)

        for event in events:
            self.encode_pipeline.transform(event)
            if event.vec is None:
                raise ValueError(
                    f"EncodePipeline did not set vec for event: {event}"
                )
            grouped[event.user_username].append(event)

        sequences: List[list] = []
        for user_events in grouped.values():
            user_events.sort(key=lambda e: e.timestamp_as_datetime())

            for i in range(len(user_events) - self.seq_len + 1):
                window = user_events[i:i + self.seq_len]
                sequences.append([e.vec for e in window])

        return sequences

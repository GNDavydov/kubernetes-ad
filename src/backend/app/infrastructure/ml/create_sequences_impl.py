from collections import defaultdict
from typing import List, Tuple

import numpy as np

from app.domain.entities.audit_event import AuditEvent
from app.domain.interfaces.create_sequences import CreateSequences
from app.domain.interfaces.encode_pipeline import EncodePipeline


class CreateSequencesImpl(CreateSequences):
    def __init__(self, encode_pipeline: EncodePipeline, seq_len: int) -> None:
        self.encode_pipeline = encode_pipeline
        self.seq_len = seq_len

    def shape(self) -> Tuple[int, int]:
        return (self.seq_len, self.encode_pipeline.shape())

    def transform(self, events: list[AuditEvent]) -> np.ndarray:
        grouped: dict[str, List[AuditEvent]] = defaultdict(list)

        for event in events:
            self.encode_pipeline.transform(event)
            if event.vec is None:
                raise ValueError(
                    f"EncodePipeline did not set vec for event: {event}"
                )
            grouped[event.user_username].append(event)

        sequences = []

        for user_events in grouped.values():
            user_events.sort(key=lambda e: e.timestamp_as_datetime())
            user_vecs = np.array([e.vec for e in user_events])

            if len(user_vecs) < self.seq_len:
                continue

            for i in range(len(user_vecs) - self.seq_len + 1):
                window = user_vecs[i:i + self.seq_len]
                sequences.append(window)

        return np.array(sequences)

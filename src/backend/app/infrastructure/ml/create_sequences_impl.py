from __future__ import annotations

from collections import defaultdict
from typing import List

import numpy as np

from app.domain.entities.audit_event import AuditEvent
from app.domain.entities.sequence_window import SequenceWindowDescriptor
from app.domain.interfaces.encode_pipeline import EncodePipeline


class CreateSequencesImpl:
    def __init__(self, encode_pipeline: EncodePipeline) -> None:
        self._encode_pipeline = encode_pipeline

    def transform(
        self,
        events: List[AuditEvent],
        seq_len: int,
    ) -> tuple[np.ndarray, List[SequenceWindowDescriptor]]:
        if seq_len < 2:
            raise ValueError("seq_len must be at least 2 for sequence modeling.")

        if not events:
            raise RuntimeError("No events to build sequences from.")

        self._encode_pipeline.fit()

        for event in events:
            vec = self._encode_pipeline.transform(event)
            event.vec = np.asarray(vec, dtype=np.float32)

        by_user: dict[str, list[AuditEvent]] = defaultdict(list)
        for event in events:
            by_user[event.user_username].append(event)

        rows: list[np.ndarray] = []
        descriptors: list[SequenceWindowDescriptor] = []

        for user, user_events in by_user.items():
            user_events.sort(key=lambda e: e.timestamp_as_datetime())
            n = len(user_events)
            if n < seq_len:
                continue
            for start in range(0, n - seq_len + 1):
                window = user_events[start : start + seq_len]
                stacked = np.stack([e.vec for e in window], axis=0)
                rows.append(stacked.astype(np.float32, copy=False))
                descriptors.append(
                    SequenceWindowDescriptor(
                        user_username=user,
                        start_timestamp=window[0].timestamp_as_datetime(),
                        end_timestamp=window[-1].timestamp_as_datetime(),
                    )
                )

        if not rows:
            raise RuntimeError(
                "No sequences could be formed: need at least seq_len events "
                f"({seq_len}) per at least one user after grouping."
            )

        return np.stack(rows, axis=0), descriptors

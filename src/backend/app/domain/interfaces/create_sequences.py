from typing import List, Protocol, Tuple

import numpy as np

from app.domain.entities.audit_event import AuditEvent
from app.domain.entities.sequence_window import SequenceWindowDescriptor


class CreateSequences(Protocol):
    """
    Группирует события по user_username, сортирует по времени, формирует скользящие
    окна длины seq_len и возвращает массив (N, seq_len, input_dim) и дескрипторы окон.
    """

    def transform(
        self,
        events: List[AuditEvent],
        seq_len: int,
    ) -> Tuple[np.ndarray, List[SequenceWindowDescriptor]]:
        ...

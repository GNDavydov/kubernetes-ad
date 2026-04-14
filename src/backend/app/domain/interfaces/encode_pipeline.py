from typing import Protocol, List

from app.domain.entities.audit_dataset import AuditDataset


class EncodePipeline(Protocol):
    def fit(self) -> None:
        ...

    def transform(self, dataset: AuditDataset) -> List:
        ...

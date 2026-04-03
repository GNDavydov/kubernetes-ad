from enum import StrEnum


class ModelStatus(StrEnum):
    CREATED = "created"
    TRAINING = "training"
    READY = "ready"
    DETECTING = "detecting"
    FAILED = "failed"

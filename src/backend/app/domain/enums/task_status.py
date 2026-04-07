from enum import StrEnum


class TaskStatus(StrEnum):
    STARTING = "starting"
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELED = "canceled"

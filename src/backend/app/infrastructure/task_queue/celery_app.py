from uuid import UUID
from typing import Callable

from celery import Celery

from app.domain.interfaces.task_queue import TaskQueue


class CeleryTaskQueue(TaskQueue):
    def __init__(self, app_name: str, broker_url: str, backend_url: str) -> None:
        self.app = Celery(
            app_name,
            broker=broker_url,
            backend=backend_url
        )
        self.app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="Europe/Amsterdam",
            enable_utc=True,
        )
        self._detect_task = None
        self._train_task = None

    def register_detect_task(self, detect_task: Callable[[UUID, UUID], None]):
        task = self.app.task(name="app.detect_task")(detect_task)
        self._detect_task = task
        return task

    def register_train_task(self, train_task: Callable[[UUID, UUID], None]):
        task = self.app.task(name="app.train_task")(train_task)
        self._train_task = task
        return task

    def detect_task(self, model_id: UUID, integration_id: UUID) -> None:
        if self._detect_task is None:
            raise RuntimeError("detect_task is not registered")

        self._detect_task.delay(model_id, integration_id)

    def train_task(self, model_id: UUID, integration_id: UUID) -> None:
        if self._train_task is None:
            raise RuntimeError("train_task is not registered")

        self._train_task.delay(model_id, integration_id)

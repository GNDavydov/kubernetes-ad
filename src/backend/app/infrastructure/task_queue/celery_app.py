from typing import Callable
from uuid import UUID

from celery import Celery

from app.domain.interfaces.task_queue import TaskQueue


class CeleryTaskQueue(TaskQueue):
    def __init__(
        self,
        app_name: str,
        broker_url: str,
        backend_url: str,
        train_task_name: str = "app.train_task",
        detect_task_name: str = "app.detect_task",
    ) -> None:
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
        self.train_task_name = train_task_name
        self.detect_task_name = detect_task_name
        self._detect_task = None
        self._train_task = None

    def register_detect_task(self, detect_task: Callable[[UUID | str], None]):
        task = self.app.task(name=self.detect_task_name)(detect_task)
        self._detect_task = task
        return task

    def register_train_task(self, train_task: Callable[[UUID | str], None]):
        task = self.app.task(name=self.train_task_name)(train_task)
        self._train_task = task
        return task

    def detect_task(self, task_id: UUID) -> None:
        self.app.send_task(self.detect_task_name, args=[task_id])

    def train_task(self, task_id: UUID) -> None:
        self.app.send_task(self.train_task_name, args=[task_id])

from uuid import uuid4
import asyncio
from datetime import datetime

from app.domain.interfaces.task_queue import TaskQueue


class UseClassCreateTask:
    def __init__(self, queue: TaskQueue) -> None:
        self.queue = queue

    async def scheduler_loop(self):
        while True:
            try:
                self.run_detection_scheduler()
            except Exception as e:
                print(f"Scheduler error: {e}")
            await asyncio.sleep(10)

    def run_detection_scheduler(self):
        self.queue.detect_task(model_id=uuid4(), integration_id=uuid4())

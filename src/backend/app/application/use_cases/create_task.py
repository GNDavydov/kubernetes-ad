import asyncio

from app.domain.enums.task_status import TaskStatus
from app.domain.enums.task_type import TaskType
from app.domain.repositories.task_repository import TaskRepository
from app.domain.interfaces.task_queue import TaskQueue


class CreateTaskUseCase:
    def __init__(self, queue: TaskQueue, task_repository: TaskRepository) -> None:
        self.queue = queue
        self.task_repository = task_repository

    async def scheduler_loop(self) -> None:
        while True:
            try:
                await self.run_detection_scheduler()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"Scheduler error: {exc}")
            await asyncio.sleep(10)

    async def run_detection_scheduler(self) -> None:
        tasks = await self.task_repository.list_by_status(status=TaskStatus.STARTING)
        print(f"Обнаружено: {len(tasks)} задач")
        for task in tasks:
            if task.id is None:
                continue
            if task.type == TaskType.DETECT:
                self.queue.detect_task(task.id)
                await self.task_repository.update_status(
                    task_id=task.id,
                    status=TaskStatus.PENDING,
                )
                print(f"Задача {task.id} типа {task.type} создана")
            elif task.type == TaskType.TRAIN:
                self.queue.train_task(task.id)
                await self.task_repository.update_status(
                    task_id=task.id,
                    status=TaskStatus.PENDING,
                )
                print(f"Задача {task.id} типа {task.type} создана")

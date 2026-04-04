from app.core.settings import get_settings
from app.infrastructure.task_queue.celery_app import CeleryTaskQueue
from app.application.use_cases.train import train
from app.application.use_cases.detect import detect

settings = get_settings()

if __name__ == "__main__":
    task_queue = CeleryTaskQueue(
        app_name=settings.app_name,
        broker_url=settings.celery_broker_url,
        backend_url=settings.celery_result_backend
    )
    task_queue.register_detect_task(detect_task=detect)
    task_queue.register_train_task(train_task=train)
    argv: list[str] = [
        "worker",
        "--loglevel=info",
        "--pool=solo"
    ]
    task_queue.app.worker_main(argv)

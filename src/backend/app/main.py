import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from app.api.routers import (
    integrations_router,
    metrics_router,
    models_router,
    task_results_router,
    tasks_router,
)
from app.application.exceptions import ResourceNotFoundError
from app.application.use_cases.create_task import UseClassCreateTask
from app.application.use_cases.train import train
from app.application.use_cases.detect import detect
from app.core.settings import get_settings
from app.infrastructure.db.database import Database
from app.infrastructure.task_queue.celery_app import CeleryTaskQueue


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    database = Database(
        settings.database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )
    app.state.database = database
    await database.init_db()
    task_queue = CeleryTaskQueue(
        app_name=settings.app_name,
        broker_url=settings.celery_broker_url,
        backend_url=settings.celery_result_backend
    )
    task_queue.register_detect_task(detect_task=detect)
    task_queue.register_train_task(train_task=train)
    create_task = UseClassCreateTask(queue=task_queue)
    task = asyncio.create_task(create_task.scheduler_loop())
    yield
    task.cancel()
    await database.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(
    _: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


app.include_router(integrations_router)
app.include_router(models_router)
app.include_router(tasks_router)
app.include_router(metrics_router)
app.include_router(task_results_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.api_host,
                port=settings.api_port, reload=True)

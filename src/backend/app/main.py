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
from app.core.settings import get_settings
from app.infrastructure.db.database import Database

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
    yield
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

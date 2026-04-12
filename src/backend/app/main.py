import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import uvicorn

from app.api.routes import (
    auth_router,
    integrations_router,
    models_router,
    profile_router,
    tasks_router,
    users_router,
)
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.ensure_admin_exists import EnsureAdminExistsUseCase
from app.application.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from app.core.settings import get_settings
from app.infrastructure.db.database import Database
from app.infrastructure.db.repositories.task_repository_impl import TaskRepositoryImpl
from app.infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.task_queue.celery_app import CeleryTaskQueue
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.infrastructure.security.password_hasher import PasswordHasherImpl
from app.infrastructure.security.redis_token_blacklist import RedisTokenBlacklist


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    database = Database(
        settings.database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )
    password_hasher = PasswordHasherImpl()
    token_service = JwtTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
    )
    token_blacklist = RedisTokenBlacklist.from_url(
        redis_url=settings.redis_blacklist_url,
        key_prefix=settings.redis_blacklist_key_prefix,
    )

    app.state.database = database
    app.state.password_hasher = password_hasher
    app.state.token_service = token_service
    app.state.token_blacklist = token_blacklist

    await database.init_db()

    task_queue = CeleryTaskQueue(
        app_name=settings.app_name,
        broker_url=settings.celery_broker_url,
        backend_url=settings.celery_result_backend
    )
    scheduler_session = database.session_factory()
    task_repository = TaskRepositoryImpl(scheduler_session)
    create_task = CreateTaskUseCase(
        queue=task_queue,
        task_repository=task_repository,
    )
    scheduler_task = asyncio.create_task(create_task.scheduler_loop())

    async for session in database.get_db():
        user_repository = UserRepositoryImpl(session)
        ensure_admin_exists_use_case = EnsureAdminExistsUseCase(
            user_repository=user_repository,
            password_hasher=password_hasher,
        )
        await ensure_admin_exists_use_case.execute(
            admin_email=settings.admin_email,
            admin_password=settings.admin_password,
        )
        break

    yield
    scheduler_task.cancel()
    with suppress(asyncio.CancelledError):
        await scheduler_task
    await scheduler_session.close()
    await token_blacklist.aclose()
    await database.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(
    _: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.detail})


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(
    _: Request, exc: AuthenticationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail},
    )


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(
    _: Request, exc: AuthorizationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.detail},
    )


@app.exception_handler(ConflictError)
async def conflict_error_handler(_: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(_: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.detail},
    )

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profile_router)
app.include_router(models_router)
app.include_router(integrations_router)
app.include_router(tasks_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.api_host,
                port=settings.api_port, reload=True)

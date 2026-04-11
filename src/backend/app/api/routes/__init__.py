from app.api.routes.auth import router as auth_router
from app.api.routes.integrations import router as integrations_router
from app.api.routes.models import router as models_router
from app.api.routes.profile import router as profile_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.users import router as users_router

__all__ = [
    "auth_router",
    "users_router",
    "profile_router",
    "models_router",
    "integrations_router",
    "tasks_router",
]

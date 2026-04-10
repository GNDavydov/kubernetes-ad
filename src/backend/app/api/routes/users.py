from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import require_admin
from app.api.dependencies.services import get_user_service
from app.api.schemas.user import (
    AdminSetPasswordRequest,
    CreateUserRequest,
    MessageResponse,
    UserResponse,
)
from app.application.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(
        get_user_service
    ),
) -> UserResponse:
    user = await user_service.create(
        email=request.email,
        password=request.password,
        role=request.role,
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )


@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[Depends(require_admin)],
)
async def list_users(
    user_service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    users = await user_service.list_users()
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )
        for user in users
    ]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
)
async def get_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await user_service.get_user_by_id(user_id)
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )


@router.post(
    "/{user_id}/set-password",
    response_model=MessageResponse,
    dependencies=[Depends(require_admin)],
)
async def set_user_password(
    user_id: UUID,
    request: AdminSetPasswordRequest,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    await user_service.admin_set_password(
        user_id=user_id,
        new_password=request.new_password,
    )
    return MessageResponse(detail="Password updated successfully")

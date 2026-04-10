import time

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import (
    get_authenticate_user_use_case,
    get_current_token_payload,
    get_token_blacklist,
)
from app.api.schemas.auth import TokenResponse
from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.api.schemas.user import MessageResponse
from app.domain.entities.access_token_payload import AccessTokenPayload
from app.domain.interfaces.token_blacklist import TokenBlacklist

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    authenticate_user_use_case: AuthenticateUserUseCase = Depends(
        get_authenticate_user_use_case
    ),
) -> TokenResponse:
    access_token = await authenticate_user_use_case.execute(
        email=form_data.username,
        password=form_data.password,
    )
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: AccessTokenPayload = Depends(get_current_token_payload),
    token_blacklist: TokenBlacklist = Depends(get_token_blacklist),
) -> MessageResponse:
    ttl_seconds = max(0, int(payload.exp - int(time.time())))
    await token_blacklist.revoke(payload.jti, ttl_seconds)
    return MessageResponse(detail="Logged out successfully")

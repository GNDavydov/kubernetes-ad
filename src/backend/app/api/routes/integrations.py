from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_integration_service
from app.api.schemas.integration import (
    CreateIntegrationRequest,
    IntegrationResponse,
    UpdateIntegrationRequest,
)
from app.api.schemas.user import MessageResponse
from app.application.services.integration_service import IntegrationService
from app.domain.entities.integration import Integration
from app.domain.entities.user import User

router = APIRouter(prefix="/integrations", tags=["integrations"])


def _to_response(integration: Integration) -> IntegrationResponse:
    return IntegrationResponse(
        id=integration.id,
        user_id=integration.user_id,
        name=integration.name,
        url=integration.url,
        username=integration.username,
        log_source_name=integration.log_source_name,
        anomaly_name=integration.anomaly_name,
        created_at=integration.created_at,
    )


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    request: CreateIntegrationRequest,
    current_user: User = Depends(get_current_user),
    integration_service: IntegrationService = Depends(get_integration_service),
) -> IntegrationResponse:
    integration = await integration_service.create(
        user_id=current_user.id,
        name=request.name,
        url=request.url,
        username=request.username,
        password=request.password,
        log_source_name=request.log_source_name,
        anomaly_name=request.anomaly_name,
    )
    return _to_response(integration)


@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    integration_service: IntegrationService = Depends(get_integration_service),
) -> list[IntegrationResponse]:
    integrations = await integration_service.list_my(user_id=current_user.id)
    return [_to_response(integration) for integration in integrations]


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration_by_id(
    integration_id: UUID,
    current_user: User = Depends(get_current_user),
    integration_service: IntegrationService = Depends(get_integration_service),
) -> IntegrationResponse:
    integration = await integration_service.get_my_by_id(
        user_id=current_user.id,
        integration_id=integration_id,
    )
    return _to_response(integration)


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    request: UpdateIntegrationRequest,
    current_user: User = Depends(get_current_user),
    integration_service: IntegrationService = Depends(get_integration_service),
) -> IntegrationResponse:
    integration = await integration_service.update_my(
        user_id=current_user.id,
        integration_id=integration_id,
        name=request.name,
        url=request.url,
        username=request.username,
        password=request.password,
        log_source_name=request.log_source_name,
        anomaly_name=request.anomaly_name,
    )
    return _to_response(integration)


@router.delete("/{integration_id}", response_model=MessageResponse)
async def delete_integration(
    integration_id: UUID,
    current_user: User = Depends(get_current_user),
    integration_service: IntegrationService = Depends(get_integration_service),
) -> MessageResponse:
    await integration_service.delete_my(
        user_id=current_user.id,
        integration_id=integration_id,
    )
    return MessageResponse(detail="Integration deleted successfully")

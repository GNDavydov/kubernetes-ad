from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_integration_service
from app.api.schemas.integration import (
    IntegrationCreateSchema,
    IntegrationPatchSchema,
    IntegrationPutSchema,
    IntegrationReadSchema,
)
from app.application.services.integration_service import IntegrationService


router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("", response_model=IntegrationReadSchema, status_code=status.HTTP_201_CREATED)
async def create_integration(
    payload: IntegrationCreateSchema,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationReadSchema:
    created = await service.create(
        name=payload.name,
        url=payload.url,
        username=payload.username,
        password=payload.password,
        index_name=payload.index_name,
    )
    return IntegrationReadSchema.model_validate(created)


@router.get("", response_model=list[IntegrationReadSchema])
async def list_integrations(
    service: IntegrationService = Depends(get_integration_service),
) -> list[IntegrationReadSchema]:
    integrations = await service.list_all()
    return [IntegrationReadSchema.model_validate(item) for item in integrations]


@router.get("/{integration_id}", response_model=IntegrationReadSchema)
async def get_integration(
    integration_id: UUID,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationReadSchema:
    integration = await service.get(integration_id)
    return IntegrationReadSchema.model_validate(integration)


@router.put("/{integration_id}", response_model=IntegrationReadSchema)
async def put_integration(
    integration_id: UUID,
    payload: IntegrationPutSchema,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationReadSchema:
    updated = await service.replace(
        integration_id=integration_id,
        name=payload.name,
        url=payload.url,
        username=payload.username,
        password=payload.password,
        index_name=payload.index_name,
    )
    return IntegrationReadSchema.model_validate(updated)


@router.patch("/{integration_id}", response_model=IntegrationReadSchema)
async def patch_integration(
    integration_id: UUID,
    payload: IntegrationPatchSchema,
    service: IntegrationService = Depends(get_integration_service),
) -> IntegrationReadSchema:
    patch = payload.model_dump(exclude_unset=True)
    updated = await service.partial_update(integration_id, patch)
    return IntegrationReadSchema.model_validate(updated)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: UUID,
    service: IntegrationService = Depends(get_integration_service),
) -> None:
    await service.delete(integration_id)

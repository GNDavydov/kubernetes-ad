from uuid import UUID

from app.application.exceptions import ResourceNotFoundError
from app.domain.entities.integration import Integration
from app.domain.repositories.integration_repository import IntegrationRepository


class IntegrationService:
    def __init__(self, integration_repository: IntegrationRepository) -> None:
        self._integration_repository = integration_repository

    async def create(
        self,
        user_id: UUID,
        name: str,
        url: str,
        username: str | None,
        password: str | None,
        log_source_name: str,
        anomaly_name: str,
    ) -> Integration:
        integration = Integration(
            id=None,
            user_id=user_id,
            name=name,
            url=url,
            username=username,
            password=password,
            log_source_name=log_source_name,
            anomaly_name=anomaly_name,
            created_at=None,
        )
        return await self._integration_repository.create(integration)

    async def list_my(self, user_id: UUID) -> list[Integration]:
        return await self._integration_repository.list_by_user(user_id)

    async def get_my_by_id(self, user_id: UUID, integration_id: UUID) -> Integration:
        integration = await self._integration_repository.get_by_id(integration_id)
        if integration is None or integration.user_id != user_id:
            raise ResourceNotFoundError("Integration not found")
        return integration

    async def update_my(
        self,
        user_id: UUID,
        integration_id: UUID,
        name: str | None = None,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        log_source_name: str | None = None,
        anomaly_name: str | None = None,
    ) -> Integration:
        existing_integration = await self.get_my_by_id(
            user_id=user_id,
            integration_id=integration_id,
        )

        if existing_integration is None:
            raise ResourceNotFoundError("Integration not found")

        updated_integration = Integration(
            id=existing_integration.id,
            user_id=existing_integration.user_id,
            name=name if name is not None else existing_integration.name,
            url=url if url is not None else existing_integration.url,
            username=username if username is not None else existing_integration.username,
            password=password if password is not None else existing_integration.password,
            log_source_name=log_source_name if log_source_name is not None else existing_integration.log_source_name,
            anomaly_name=anomaly_name if anomaly_name is not None else existing_integration.anomaly_name,
            created_at=existing_integration.created_at,
        )

        updated = await self._integration_repository.update(updated_integration)
        if updated is None:
            raise ResourceNotFoundError("Integration not found")
        return updated

    async def delete_my(self, user_id: UUID, integration_id: UUID) -> None:
        _ = await self.get_my_by_id(user_id=user_id, integration_id=integration_id)
        await self._integration_repository.delete(integration_id)

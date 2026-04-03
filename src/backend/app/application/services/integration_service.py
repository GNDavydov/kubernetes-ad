from datetime import datetime, timezone
from typing import Any, List
from uuid import UUID

from app.application.exceptions import ResourceNotFoundError
from app.domain.entities.integration import Integration
from app.domain.repositories.integration_repository import IntegrationRepository


class IntegrationService:
    def __init__(self, repository: IntegrationRepository) -> None:
        self._repository = repository

    async def create(
        self,
        name: str,
        url: str,
        username: str,
        password: str,
        index_name: str,
    ) -> Integration:
        entity = Integration(
            id=None,
            name=name,
            url=url,
            username=username,
            password=password,
            index_name=index_name,
            created_at=datetime.now(timezone.utc),
        )
        return await self._repository.add(entity)

    async def list_all(self) -> List[Integration]:
        return await self._repository.list()

    async def get(self, integration_id: UUID) -> Integration:
        integration = await self._repository.get_by_id(integration_id)
        if integration is None:
            raise ResourceNotFoundError("Integration not found")
        return integration

    async def replace(
        self,
        integration_id: UUID,
        name: str,
        url: str,
        username: str,
        password: str,
        index_name: str,
    ) -> Integration:
        current = await self._repository.get_by_id(integration_id)
        if current is None:
            raise ResourceNotFoundError("Integration not found")

        entity = Integration(
            id=integration_id,
            name=name,
            url=url,
            username=username,
            password=password,
            index_name=index_name,
            created_at=current.created_at,
        )
        return await self._repository.update(entity)

    async def partial_update(self, integration_id: UUID, patch: dict[str, Any]) -> Integration:
        current = await self._repository.get_by_id(integration_id)
        if current is None:
            raise ResourceNotFoundError("Integration not found")

        entity = Integration(
            id=integration_id,
            name=patch.get("name", current.name),
            url=patch.get("url", current.url),
            username=patch.get("username", current.username),
            password=patch.get("password", current.password),
            index_name=patch.get("index_name", current.index_name),
            created_at=current.created_at,
        )

        try:
            return await self._repository.update(entity)
        except ValueError as exc:
            raise ResourceNotFoundError("Integration not found") from exc

    async def delete(self, integration_id: UUID) -> None:
        current = await self._repository.get_by_id(integration_id)
        if current is None:
            raise ResourceNotFoundError("Integration not found")
        await self._repository.delete(integration_id)

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.integration import Integration
from app.domain.repositories.integration_repository import IntegrationRepository
from app.infrastructure.db.models.integration import IntegrationModel


class IntegrationRepositoryImpl(IntegrationRepository):

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, integration: Integration) -> Integration:
        db_integration = IntegrationModel(
            user_id=integration.user_id,
            name=integration.name,
            url=integration.url,
            username=integration.username,
            password=integration.password,
            index_name=integration.index_name,
            created_at=integration.created_at or datetime.now(timezone.utc),
        )
        self.db.add(db_integration)
        await self.db.commit()
        await self.db.refresh(db_integration)
        return self._to_entity(db_integration)

    async def list(self) -> List[Integration]:
        result = await self.db.execute(select(IntegrationModel))
        db_integrations = result.scalars().all()
        return [self._to_entity(db_integration) for db_integration in db_integrations]

    async def get_by_id(self, integration_id: UUID) -> Integration | None:
        db_integration = await self.db.get(IntegrationModel, integration_id)
        return self._to_entity(db_integration) if db_integration else None

    async def list_by_user(self, user_id: UUID) -> List[Integration]:
        result = await self.db.execute(
            select(IntegrationModel).where(IntegrationModel.user_id == user_id)
        )
        db_integrations = result.scalars().all()
        return [self._to_entity(db_integration) for db_integration in db_integrations]

    async def update(self, integration: Integration) -> Integration:
        if integration.id is None:
            raise ValueError("Integration id is required for update")
        db_integration = await self.db.get(IntegrationModel, integration.id)
        if db_integration is None:
            raise ValueError(f"Integration with id={integration.id} not found")

        db_integration.user_id = integration.user_id
        db_integration.name = integration.name
        db_integration.url = integration.url
        db_integration.username = integration.username
        db_integration.password = integration.password
        db_integration.index_name = integration.index_name
        await self.db.commit()
        await self.db.refresh(db_integration)
        return self._to_entity(db_integration)

    async def delete(self, integration_id: UUID) -> None:
        db_integration = await self.db.get(IntegrationModel, integration_id)
        if db_integration:
            await self.db.delete(db_integration)
            await self.db.commit()

    @staticmethod
    def _to_entity(db_integration: IntegrationModel) -> Integration:
        return Integration(
            id=db_integration.id,
            user_id=db_integration.user_id,
            name=db_integration.name,
            url=db_integration.url,
            username=db_integration.username,
            password=db_integration.password,
            index_name=db_integration.index_name,
            created_at=db_integration.created_at
        )

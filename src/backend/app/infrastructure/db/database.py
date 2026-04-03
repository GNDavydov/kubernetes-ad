from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.db.models.base import Base


class Database:
    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    async def init_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def get_db(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session

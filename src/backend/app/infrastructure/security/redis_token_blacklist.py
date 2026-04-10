from __future__ import annotations

from redis.asyncio import Redis
from redis.asyncio import from_url as redis_from_url

from app.domain.interfaces.token_blacklist import TokenBlacklist


class RedisTokenBlacklist(TokenBlacklist):
    def __init__(
        self,
        redis_client: Redis,
        key_prefix: str = "auth:blacklist:",
        owns_client: bool = False,
    ) -> None:
        self._redis = redis_client
        self._key_prefix = key_prefix
        self._owns_client = owns_client

    @classmethod
    def from_url(
        cls,
        redis_url: str,
        key_prefix: str = "auth:blacklist:",
        decode_responses: bool = True,
    ) -> RedisTokenBlacklist:
        redis_client = redis_from_url(
            redis_url, decode_responses=decode_responses)
        return cls(
            redis_client=redis_client,
            key_prefix=key_prefix,
            owns_client=True,
        )

    def _key(self, jti: str) -> str:
        return f"{self._key_prefix}{jti}"

    async def is_revoked(self, jti: str) -> bool:
        return bool(await self._redis.exists(self._key(jti)))

    async def revoke(self, jti: str, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        await self._redis.set(self._key(jti), "1", ex=ttl_seconds)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._redis.aclose()

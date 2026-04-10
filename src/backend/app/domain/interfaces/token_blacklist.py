from typing import Protocol


class TokenBlacklist(Protocol):
    async def is_revoked(self, jti: str) -> bool:
        ...

    async def revoke(self, jti: str, ttl_seconds: int) -> None:
        ...

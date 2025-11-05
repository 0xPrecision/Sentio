from __future__ import annotations
from redis.asyncio import Redis

class Idempotency:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def once(self, key: str, ttl_sec: int = 24 * 3600) -> bool:
        return await self.redis.set(name=key, value="1", nx=True, ex=ttl_sec) is True

async def get_idem(redis: Redis) -> "Idempotency":
    return Idempotency(redis)

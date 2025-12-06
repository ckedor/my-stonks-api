import json
from typing import Optional

from redis.asyncio import Redis

from app.config.settings import settings


class RedisService:
    def __init__(self):
        self.client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.prefix = 'cache'

    def _format_key(self, key: str) -> str:
        return f'{self.prefix}:{key}'

    async def set_json(self, key: str, value: dict, expire_seconds: Optional[int] = None) -> None:
        full_key = self._format_key(key)
        if isinstance(value, str):
            data = value
        else:
            data = json.dumps(value, allow_nan=False)
        await self.client.set(full_key, data, ex=expire_seconds)

    async def get_json(self, key: str) -> Optional[dict]:
        full_key = self._format_key(key)
        data = await self.client.get(full_key)
        if data:
            return json.loads(data)
        return None

    async def delete(self, key: str) -> None:
        full_key = self._format_key(key)
        await self.client.delete(full_key)

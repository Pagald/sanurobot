import logging
import info
from typing import Any, Optional

try:
    import orjson as json_mod
    def _dumps(obj):
        return json_mod.dumps(obj).decode('utf-8')
    def _loads(s):
        return json_mod.loads(s)
except ImportError:
    import json as json_mod
    def _dumps(obj):
        return json_mod.dumps(obj)
    def _loads(s):
        return json_mod.loads(s)

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    aioredis = None
    HAS_REDIS = False

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self._redis = None
        self._is_connected = False

    async def get_client(self):
        if not HAS_REDIS or not getattr(info, 'REDIS_URI', None):
            return None
        if self._redis is None:
            try:
                uri = info.REDIS_URI.strip()
                if uri.startswith("redis-cli -u "):
                    uri = uri.replace("redis-cli -u ", "").strip()
                self._redis = aioredis.from_url(
                    uri,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                await self._redis.ping()
                self._is_connected = True
                logger.info("[REDIS] Connected to Redis RAM Cache successfully!")
            except Exception as e:
                logger.warning(f"[REDIS] Connection failed: {e}. Falling back to DB.")
                self._redis = None
                self._is_connected = False
        return self._redis

    async def get_json_cache(self, key: str) -> Optional[Any]:
        try:
            client = await self.get_client()
            if not client:
                return None
            val = await client.get(key)
            if val:
                return _loads(val)
        except Exception as e:
            logger.debug(f"Redis get_json_cache error [{key}]: {e}")
        return None

    async def set_json_cache(self, key: str, value: Any, ttl: int = 600) -> bool:
        try:
            client = await self.get_client()
            if not client:
                return False
            serialized = _dumps(value)
            await client.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.debug(f"Redis set_json_cache error [{key}]: {e}")
        return False

    async def delete_cache(self, key: str) -> bool:
        try:
            client = await self.get_client()
            if not client:
                return False
            await client.delete(key)
            return True
        except Exception as e:
            logger.debug(f"Redis delete_cache error [{key}]: {e}")
        return False

    async def delete_pattern(self, pattern: str) -> bool:
        try:
            client = await self.get_client()
            if not client:
                return False
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
            return True
        except Exception as e:
            logger.debug(f"Redis delete_pattern error [{pattern}]: {e}")
        return False

redis_db = RedisCache()

"""Redis cache helpers. The app continues to work if Redis is unavailable."""
import json
import os
import logging
from typing import Any

logger = logging.getLogger(__name__)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
_client = None

def get_redis():
    global _client
    if _client is not None:
        return _client
    try:
        import redis
        client = redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        _client = client
        return _client
    except Exception as exc:
        logger.warning("Redis unavailable; cache disabled for this request: %s", exc)
        return None

def cache_get(key: str) -> Any | None:
    client = get_redis()
    if client is None:
        return None
    try:
        value = client.get(key)
        return json.loads(value) if value else None
    except Exception as exc:
        logger.warning("Redis cache read failed: %s", exc)
        return None

def cache_set(key: str, value: Any, ttl: int = CACHE_TTL_SECONDS) -> None:
    client = get_redis()
    if client is None:
        return
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        logger.warning("Redis cache write failed: %s", exc)

def cache_delete(*keys: str) -> None:
    client = get_redis()
    if client is None or not keys:
        return
    try:
        client.delete(*keys)
    except Exception as exc:
        logger.warning("Redis cache invalidation failed: %s", exc)

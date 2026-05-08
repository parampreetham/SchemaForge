"""Redis connection management."""

import redis

from app.core import settings


def get_redis_client() -> redis.Redis:
    """Create and return a Redis client connection."""
    return redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )


# Singleton Redis client for the application
redis_client = get_redis_client()

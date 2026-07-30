import redis.asyncio as redis

from app.config.settings import settings


async def init_redis_pool() -> redis.Redis:
    pool = redis.ConnectionPool(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True,
        max_connections=20,
    )
    return redis.Redis(connection_pool=pool)

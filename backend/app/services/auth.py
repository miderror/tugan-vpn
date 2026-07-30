import hashlib
import hmac
import secrets
import time

import msgspec
import redis.asyncio as redis
from fast_query_parsers import parse_query_string

from app.config.settings import settings

TG_SECRET_KEY = hmac.new(
    b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256
).digest()


SESSION_ENCODER = msgspec.json.Encoder()


def validate_init_data(init_data: bytes) -> dict | None:
    try:
        parsed_data = dict(parse_query_string(init_data, separator="&"))
        if not parsed_data:
            return None

        received_hash = parsed_data.pop("hash", None)
        if not received_hash:
            return None

        auth_date = int(parsed_data.get("auth_date", 0))
        if abs(int(time.time()) - auth_date) > 86400:
            return None

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        ).encode()

        computed_hash = hmac.new(
            TG_SECRET_KEY, data_check_string, hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(computed_hash, received_hash):
            return parsed_data

        return None
    except (ValueError, KeyError, TypeError):
        return None


async def get_active_session(redis_client: redis.Redis, tg_id: int) -> str | None:
    return await redis_client.get(f"session:{tg_id}")


async def create_session(redis_client: redis.Redis, tg_id: int) -> str:
    user_key = f"session:{tg_id}"
    session_token = f"{tg_id}:{secrets.token_hex(16)}"
    await redis_client.setex(user_key, 86400, session_token)
    return session_token


async def validate_session(redis_client: redis.Redis, token: str) -> int | None:
    if len(token) < 34:
        return None

    tg_id_str = token[:-33]
    if not tg_id_str.isdigit():
        return None

    tg_id = int(tg_id_str)
    stored_token: str | None = await redis_client.get(f"session:{tg_id}")
    if stored_token and stored_token == token:
        return tg_id

    return None

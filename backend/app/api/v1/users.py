from typing import Any

import msgspec
from litestar import Controller, Request, Response, get
from litestar.status_codes import HTTP_401_UNAUTHORIZED
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

from app.services.auth import validate_session

db_engine = engine_finder()


class UserMeResponse(msgspec.Struct, gc=False, omit_defaults=True):
    access_token: str = msgspec.field(name="at")
    used_bytes: int = msgspec.field(name="ub")
    expiry_date: str = msgspec.field(name="exp")
    flags: int = msgspec.field(name="f")
    ip: str


RESPONSE_ENCODER = msgspec.json.Encoder()


class UserController(Controller):
    path = "/users"

    @get("/me")
    async def get_me(self, request: Request[Any, Any, Any]) -> Response:
        session_key = request.headers.get("X-Session-Key")
        if not session_key:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        redis_client = request.app.state.redis
        tg_id = await validate_session(redis_client, session_key)
        if not tg_id:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        user_rows = await db_engine.run_querystring(
            QueryString(
                """
                SELECT access_token, used_bytes, expiry_date,
                       ((claimed_gift::int) 
                        | (tried_to_connect::int << 1) 
                        | (is_active_vpn::int << 2)) AS flags
                FROM core_user WHERE tg_id = {}
                """,
                tg_id,
            )
        )

        if not user_rows:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        user = user_rows[0]
        xff = request.headers.get("x-forwarded-for")
        client_ip = xff.partition(",")[0].strip() if xff else "127.0.0.1"

        payload = UserMeResponse(
            access_token=user["access_token"],
            used_bytes=user["used_bytes"],
            expiry_date=user["expiry_date"].isoformat(),
            flags=user["flags"],
            ip=client_ip,
        )

        return Response(
            RESPONSE_ENCODER.encode(payload),
            media_type="application/json",
        )

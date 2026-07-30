from datetime import datetime
from typing import Any

import msgspec
from litestar import Controller, Request, Response, get
from litestar.status_codes import HTTP_401_UNAUTHORIZED
from piccolo.engine import engine_finder

from app.services.auth import get_session_tg_id

db_engine = engine_finder()


class UserMeResponse(msgspec.Struct, omit_defaults=True):
    ub: int
    exp: datetime
    act: bool
    ip: str


class UserController(Controller):
    path = "/users"

    @get("/me")
    async def get_me(
        self, request: Request[Any, Any, Any]
    ) -> UserMeResponse | Response:
        session_key = request.headers.get("x-session-key")
        if not session_key:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        tg_id = await get_session_tg_id(request.app.state.redis, session_key)
        if not tg_id:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        user_rows = await db_engine.run_raw(
            "SELECT used_bytes, expiry_date, is_active_vpn FROM core_user WHERE tg_id = $1",
            tg_id,
        )

        if not user_rows:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        user = user_rows[0]

        client_ip = request.headers.get("x-real-ip") or request.client.host or ""

        return UserMeResponse(
            ub=user["used_bytes"],
            exp=user["expiry_date"],
            act=user["is_active_vpn"],
            ip=client_ip,
        )

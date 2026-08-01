from typing import Any, ClassVar

import msgspec
from litestar import Controller, Request, Response, get
from litestar.di import Provide
from litestar.status_codes import HTTP_401_UNAUTHORIZED
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

from app.services.auth import provide_authenticated_tg_id

db_engine = engine_finder()


class UserMeResponse(msgspec.Struct, gc=False, omit_defaults=True):
    access_token: str = msgspec.field(name="at")
    used_bytes: int = msgspec.field(name="ub")
    expiry_date: str = msgspec.field(name="exp")
    flags: int = msgspec.field(name="f")
    ip: str


class ReferralResponse(msgspec.Struct, gc=False):
    total_count: int = msgspec.field(name="c")
    items: list[tuple[int, str]] = msgspec.field(name="i")


RESPONSE_ENCODER = msgspec.json.Encoder()


class UserController(Controller):
    path = "/users"
    dependencies: ClassVar[dict[str, Any]] = {
        "tg_id": Provide(provide_authenticated_tg_id)
    }

    @get("/me")
    async def get_me(self, request: Request, tg_id: int) -> Response:
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

    @get("/referrals")
    async def get_referrals(self, tg_id: int) -> Response:
        count_rows = await db_engine.run_querystring(
            QueryString(
                "SELECT COUNT(*) AS total FROM core_referral WHERE referrer_id = {}",
                tg_id,
            )
        )

        total_count: int = count_rows[0]["total"] if count_rows else 0

        if total_count == 0:
            return Response(
                RESPONSE_ENCODER.encode(ReferralResponse(total_count=0, items=[])),
                media_type="application/json",
            )

        rows = await db_engine.run_querystring(
            QueryString(
                """
                SELECT u.tg_id, COALESCE(u.username, '') AS username
                FROM core_referral r
                JOIN core_user u ON r.referred_id = u.tg_id
                WHERE r.referrer_id = {}
                ORDER BY r.referred_id DESC
                LIMIT 50
                """,
                tg_id,
            )
        )

        items = [(row["tg_id"], row["username"]) for row in rows]

        return Response(
            RESPONSE_ENCODER.encode(
                ReferralResponse(total_count=total_count, items=items)
            ),
            media_type="application/json",
        )

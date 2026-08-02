import msgspec
from litestar import Controller, Request, Response, post
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

from app.services.auth import create_session, get_active_session, validate_init_data

db_engine = engine_finder()


class TelegramUser(msgspec.Struct):
    id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    language_code: str = ""


class SessionResponse(msgspec.Struct, gc=False):
    session_key: str = msgspec.field(name="sk")


TG_USER_DECODER = msgspec.json.Decoder(TelegramUser)


class AuthController(Controller):
    path = "/auth"

    @post("/login", status_code=HTTP_200_OK)
    async def login(self, request: Request) -> SessionResponse | Response:
        init_data_str = request.headers.get("Telegram-Init-Data")
        if not init_data_str:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        validated_data = validate_init_data(init_data_str.encode())
        if not validated_data:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        tg_user_str = validated_data.get("user")
        if not tg_user_str:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        try:
            tg_user = TG_USER_DECODER.decode(tg_user_str)
        except msgspec.DecodeError:
            return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        redis_client = request.app.state.redis
        active_session = await get_active_session(redis_client, tg_user.id)
        if active_session:
            return SessionResponse(session_key=active_session)

        start_param = validated_data.get("start_param", "")
        referrer_id: int | None = None
        utm_source: str | None = None
        if start_param.startswith("ref_"):
            raw_ref = start_param[4:]
            if raw_ref.isdigit():
                referrer_id = int(raw_ref)
        elif start_param:
            utm_source = start_param[:64]

        db_result = await db_engine.run_querystring(
            QueryString(
                """
                SELECT is_new_user, referral_processed 
                FROM register_or_get_user({}, {}, {}, {}, {}, {}, {}, {}, {})
                """,
                tg_user.id,
                tg_user.username,
                tg_user.first_name,
                tg_user.last_name,
                tg_user.language_code,
                utm_source,
                referrer_id,
                7,
                14,
            )
        )

        if not db_result:
            return Response(b"", status_code=HTTP_400_BAD_REQUEST)

        row = db_result[0]
        saq_queue = getattr(request.app.state, "saq", None)
        if saq_queue:
            if row.get("is_new_user"):
                await saq_queue.enqueue("create_user_on_nodes_task", tg_id=tg_user.id)

            if row.get("referral_processed"):
                await saq_queue.enqueue("update_user_on_nodes_task", tg_id=referrer_id)
                await saq_queue.enqueue(
                    "send_referral_notification_task",
                    referrer_id=referrer_id,
                    referred_username=tg_user.username,
                )

        session_key = await create_session(redis_client, tg_user.id)
        return SessionResponse(session_key=session_key)

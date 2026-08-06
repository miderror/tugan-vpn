import base64
import time

from litestar import Controller, Response, get
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

db_engine = engine_finder()


EXPIRED_VLESS_LINK = (
    b"vless://00000000-0000-0000-0000-000000000000@127.0.0.1:1"
    b"?security=none&type=tcp#%F0%9F%9A%A8%20%D0%92%D0%B0%D1%88%D0%B0%20%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%BA%D0%B0%20%D0%BD%D0%B5%D0%B0%D0%BA%D1%82%D0%B8%D0%B2%D0%BD%D0%B0"
)
EXPIRED_SUB_B64 = base64.b64encode(EXPIRED_VLESS_LINK)


class SubscriptionController(Controller):
    path = "/api/sub"

    @get("/{access_token:str}")
    async def get_subscription(self, access_token: str) -> Response:
        if len(access_token) != 64:
            return Response(b"", status_code=HTTP_400_BAD_REQUEST)

        user_rows = await db_engine.run_querystring(
            QueryString(
                """
                SELECT client_id, used_bytes, expiry_date, is_active_vpn
                FROM core_user
                WHERE access_token = {}
                LIMIT 1
                """,
                access_token,
            )
        )

        if not user_rows:
            return Response(b"", status_code=HTTP_404_NOT_FOUND)

        user = user_rows[0]

        now_ts = int(time.time())
        expiry_ts = int(user["expiry_date"].timestamp())

        if not user["is_active_vpn"] or expiry_ts < now_ts:
            b64_payload = EXPIRED_SUB_B64
        else:
            client_id = user["client_id"]
            node_rows = await db_engine.run_querystring(
                QueryString(
                    """
                    SELECT config_template 
                    FROM core_node 
                    WHERE is_active = true AND config_template != ''
                    """
                )
            )

            configs = [
                row["config_template"].replace("{}", client_id).encode("utf-8")
                for row in node_rows
                if "{}" in row["config_template"]
            ]
            b64_payload = base64.b64encode(b"\n".join(configs))

        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Disposition": "inline",
            "profile-update-interval": "6",
            "profile-title": "base64:VFVHQU4gVlBOIPCfjI8=",
            "subscription-userinfo": (
                f"upload=0; download={user['used_bytes']}; "
                f"total=268435456000; expire={expiry_ts}"
            ),
        }

        return Response(b64_payload, headers=headers)

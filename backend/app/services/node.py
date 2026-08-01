import asyncio
from typing import Any, ClassVar

import httpx
import msgspec

from app.config.settings import settings


class XUIClient(msgspec.Struct, gc=False, omit_defaults=True):
    email: str = ""
    up: int = 0
    down: int = 0


class XUIClientSettings(msgspec.Struct, gc=False, omit_defaults=True):
    clients: list[XUIClient] = []


class XUIApiResponse(msgspec.Struct, gc=False, omit_defaults=True):
    success: bool = False
    msg: str = ""


class XUIInboundObj(msgspec.Struct, gc=False, omit_defaults=True):
    settings: str = ""


class XUIInboundResponse(msgspec.Struct, gc=False, omit_defaults=True):
    success: bool = False
    msg: str = ""
    obj: XUIInboundObj | None = None


class XUIClientPayload(msgspec.Struct, gc=False):
    id: str
    email: str
    expiryTime: int
    totalGB: int = settings.default_traffic_limit_bytes
    subId: str = ""
    limitIp: int = 1
    enable: bool = True
    flow: str = "xtls-rprx-vision"


class XUISettingsWrapper(msgspec.Struct, gc=False):
    clients: list[XUIClientPayload]


class XUIAddClientRequest(msgspec.Struct, gc=False):
    id: int
    settings: str


XUI_API_DECODER = msgspec.json.Decoder(XUIApiResponse)
XUI_INBOUND_DECODER = msgspec.json.Decoder(XUIInboundResponse)
XUI_SETTINGS_DECODER = msgspec.json.Decoder(XUIClientSettings)
JSON_ENCODER = msgspec.json.Encoder()


class NodeService:
    _session_cache: ClassVar[dict[int, str]] = {}
    _node_locks: ClassVar[dict[int, asyncio.Lock]] = {}

    @classmethod
    def _get_lock(cls, node_id: int) -> asyncio.Lock:
        lock = cls._node_locks.get(node_id)
        if lock is None:
            lock = asyncio.Lock()
            cls._node_locks[node_id] = lock
        return lock

    @classmethod
    def _build_client_payload(cls, inbound_id: int, user_data: dict) -> bytes:
        client = XUIClientPayload(
            id=user_data["client_id"],
            email=user_data["email"],
            expiryTime=int(user_data["expiry_date"].timestamp() * 1000),
            subId=user_data["sub_id"],
            enable=user_data["is_active_vpn"],
        )
        settings_str = JSON_ENCODER.encode(XUISettingsWrapper(clients=[client])).decode(
            "utf-8"
        )
        return JSON_ENCODER.encode(
            XUIAddClientRequest(id=inbound_id, settings=settings_str)
        )

    @classmethod
    async def get_session_cookie(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        force_refresh: bool = False,
    ) -> str:
        node_id: int = node["id"]
        cache_key = f"xui_sess:{node_id}"

        if not force_refresh:
            sess = cls._session_cache.get(node_id)
            if sess:
                return sess
            sess = await redis_client.get(cache_key)
            if sess:
                cls._session_cache[node_id] = sess
                return sess

        url = f"{node['api_url'].rstrip('/')}/login"
        resp = await http_client.post(
            url,
            data={"username": node["username"], "password": node["password"]},
            timeout=4.0,
        )

        set_cookie = resp.headers.get("set-cookie", "")
        end = set_cookie.find(";")
        cookie_pair = set_cookie[:end] if end != -1 else set_cookie

        if not cookie_pair:
            raise RuntimeError(f"Auth failed for node {node_id}")

        cls._session_cache[node_id] = cookie_pair
        await redis_client.setex(cache_key, 2700, cookie_pair)
        return cookie_pair

    @classmethod
    async def request_node(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        is_post: bool,
        endpoint: str,
        payload_bytes: bytes | None = None,
        decoder: msgspec.json.Decoder = XUI_API_DECODER,
    ) -> XUIApiResponse | None:
        node_id: int = node["id"]
        lock = cls._get_lock(node_id)

        async with lock:
            url = f"{node['api_url'].rstrip('/')}{endpoint}"
            force_refresh = False

            for attempt in range(2):
                try:
                    cookie = await cls.get_session_cookie(
                        http_client, redis_client, node, force_refresh
                    )
                    headers = {
                        "Cookie": cookie,
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }

                    if is_post:
                        resp = await http_client.post(
                            url, content=payload_bytes, headers=headers, timeout=5.0
                        )
                    else:
                        resp = await http_client.get(url, headers=headers, timeout=5.0)

                    if resp.status_code in (307, 401, 403):
                        force_refresh = True
                        continue

                    if resp.status_code != 200:
                        return None

                    return decoder.decode(resp.content)

                except (httpx.HTTPError, msgspec.DecodeError):
                    if attempt == 1:
                        return None
                    force_refresh = True
            return None

    @classmethod
    async def add_client_on_node(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        user_data: dict,
        payload_bytes: bytes | None = None,
    ) -> bool:
        if payload_bytes is None:
            payload_bytes = cls._build_client_payload(node["inbound_id"], user_data)

        res = await cls.request_node(
            http_client=http_client,
            redis_client=redis_client,
            node=node,
            is_post=True,
            endpoint="/panel/api/inbounds/addClient",
            payload_bytes=payload_bytes,
        )
        return bool(res and res.success)

    @classmethod
    async def update_client_on_node(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        user_data: dict,
    ) -> bool:
        req_payload = cls._build_client_payload(node["inbound_id"], user_data)

        res = await cls.request_node(
            http_client=http_client,
            redis_client=redis_client,
            node=node,
            is_post=True,
            endpoint=f"/panel/api/inbounds/updateClient/{user_data['client_id']}",
            payload_bytes=req_payload,
        )

        if res and not res.success and "empty client" in res.msg:
            return await cls.add_client_on_node(
                http_client, redis_client, node, user_data, payload_bytes=req_payload
            )
        return bool(res and res.success)

    @classmethod
    async def reset_client_traffic(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        email: str,
    ) -> bool:
        res = await cls.request_node(
            http_client=http_client,
            redis_client=redis_client,
            node=node,
            is_post=True,
            endpoint=f"/panel/api/inbounds/{node['inbound_id']}/resetClientTraffic/{email}",
        )
        return bool(res and res.success)

    @classmethod
    async def accumulate_node_traffics(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        active_emails: set[str],
        traffic_accumulator: dict[str, int],
    ) -> None:
        res: XUIInboundResponse | None = await cls.request_node(
            http_client=http_client,
            redis_client=redis_client,
            node=node,
            is_post=False,
            endpoint=f"/panel/api/inbounds/get/{node['inbound_id']}",
            decoder=XUI_INBOUND_DECODER,
        )

        if not res or not res.success or res.obj is None:
            return

        settings_raw = res.obj.settings
        del res
        if not settings_raw:
            return

        try:
            parsed_settings = XUI_SETTINGS_DECODER.decode(settings_raw)
            del settings_raw

            for client in parsed_settings.clients:
                email = client.email
                if email in active_emails:
                    bytes_used = client.up + client.down
                    if bytes_used > 0:
                        traffic_accumulator[email] = (
                            traffic_accumulator.get(email, 0) + bytes_used
                        )
        except msgspec.DecodeError:
            pass

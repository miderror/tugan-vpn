import asyncio
import logging
from collections import defaultdict
from typing import Any, ClassVar

import httpx
import msgspec

from app.config.settings import settings

logger = logging.getLogger(__name__)


class XUIClientStats(msgspec.Struct, omit_defaults=True):
    email: str = ""
    up: int = 0
    down: int = 0
    totalGB: int = 0
    enable: bool = True
    id: str = ""
    subId: str = ""
    expiryTime: int = 0


class XUISettingsParsed(msgspec.Struct, omit_defaults=True):
    clients: list[XUIClientStats] = []


class XUIInboundRaw(msgspec.Struct, omit_defaults=True):
    settings: str = ""


class XUIApiResponse(msgspec.Struct, omit_defaults=True):
    success: bool = False
    msg: str = ""
    obj: Any = None


XUI_API_DECODER = msgspec.json.Decoder(XUIApiResponse)
XUI_SETTINGS_DECODER = msgspec.json.Decoder(XUISettingsParsed)


class NodeService:
    _node_semaphores: ClassVar[defaultdict[int, asyncio.Semaphore]] = defaultdict(
        lambda: asyncio.Semaphore(2)
    )

    @classmethod
    async def get_session_cookie(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        force_refresh: bool = False,
    ) -> str:
        cache_key = f"xui_sess:{node['id']}"

        if not force_refresh:
            cookie = await redis_client.get(cache_key)
            if cookie:
                return cookie

        url = f"{node['api_url'].rstrip('/')}/login"
        resp = await http_client.post(
            url,
            data={"username": node["username"], "password": node["password"]},
            timeout=5.0,
        )

        sess = resp.cookies.get("session")
        if not sess:
            raise RuntimeError(
                f"Auth failed for node {node['id']}: HTTP {resp.status_code}"
            )

        await redis_client.setex(cache_key, 3000, sess)
        return sess

    @classmethod
    async def invalidate_session_cookie(cls, redis_client: Any, node_id: int) -> None:
        await redis_client.delete(f"xui_sess:{node_id}")

    @classmethod
    async def request_node(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        method: str,
        endpoint: str,
        json_payload: dict | None = None,
        retries: int = 1,
    ) -> XUIApiResponse | None:
        node_id = node["id"]
        sem = cls._node_semaphores[node_id]

        async with sem:
            base_url = node["api_url"].rstrip("/")
            url = f"{base_url}{endpoint}"

            for attempt in range(retries + 1):
                cookie = await cls.get_session_cookie(
                    http_client, redis_client, node, force_refresh=(attempt > 0)
                )
                headers = {
                    "Cookie": f"session={cookie}",
                    "Accept": "application/json",
                }

                try:
                    if method.upper() == "POST":
                        resp = await http_client.post(
                            url, json=json_payload, headers=headers, timeout=8.0
                        )
                    else:
                        resp = await http_client.get(url, headers=headers, timeout=10.0)

                    if resp.status_code in (
                        302,
                        307,
                    ) or "text/html" in resp.headers.get("content-type", ""):
                        await cls.invalidate_session_cookie(redis_client, node_id)
                        continue

                    if resp.status_code != 200:
                        logger.warning(
                            "Node %d returned HTTP %d for %s",
                            node_id,
                            resp.status_code,
                            endpoint,
                        )
                        continue

                    parsed = XUI_API_DECODER.decode(resp.content)

                    if (
                        not parsed.success
                        and parsed.msg
                        and any(
                            word in parsed.msg.lower()
                            for word in ("login", "session", "登录")
                        )
                    ):
                        await cls.invalidate_session_cookie(redis_client, node_id)
                        continue

                    return parsed

                except (httpx.HTTPError, msgspec.DecodeError) as err:
                    logger.error(
                        "Node request error (%s, attempt %d): %s", url, attempt, err
                    )
                    if attempt == retries:
                        return None

            return None

    @classmethod
    async def fetch_node_traffics(
        cls, http_client: httpx.AsyncClient, redis_client: Any, node: dict
    ) -> list[XUIClientStats]:
        endpoint = f"/panel/api/inbounds/get/{node['inbound_id']}"
        res = await cls.request_node(http_client, redis_client, node, "GET", endpoint)

        if not res or not res.success or not res.obj or not isinstance(res.obj, dict):
            return []

        settings_str = res.obj.get("settings")
        if not settings_str:
            return []

        try:
            settings_parsed = XUI_SETTINGS_DECODER.decode(settings_str.encode("utf-8"))
            return settings_parsed.clients
        except msgspec.DecodeError as e:
            logger.error("Failed to parse node %d settings JSON: %s", node["id"], e)
            return []

    @classmethod
    async def reset_client_node_traffic(
        cls, http_client: httpx.AsyncClient, redis_client: Any, node: dict, email: str
    ) -> bool:
        endpoint = (
            f"/panel/api/inbounds/{node['inbound_id']}/resetClientTraffic/{email}"
        )
        res = await cls.request_node(http_client, redis_client, node, "POST", endpoint)
        return bool(res and res.success)

    @classmethod
    async def upsert_and_reset_client_on_node(
        cls,
        http_client: httpx.AsyncClient,
        redis_client: Any,
        node: dict,
        user: dict,
        enable: bool = True,
        reset_traffic: bool = False,
    ) -> bool:
        expiry_ms = int(user["expiry_date"].timestamp() * 1000)

        client_dict = {
            "id": user["client_id"],
            "email": user["email"],
            "subId": user["sub_id"],
            "expiryTime": expiry_ms,
            "totalGB": settings.default_traffic_limit_bytes,
            "enable": enable,
            "limitIp": 0,
            "alterId": 0,
        }

        payload = {
            "id": node["inbound_id"],
            "settings": msgspec.json.encode({"clients": [client_dict]}).decode("utf-8"),
        }

        update_endpoint = f"/panel/api/inbounds/updateClient/{user['client_id']}"
        res = await cls.request_node(
            http_client, redis_client, node, "POST", update_endpoint, payload
        )

        if not res or not res.success:
            add_endpoint = "/panel/api/inbounds/addClient"
            res = await cls.request_node(
                http_client, redis_client, node, "POST", add_endpoint, payload
            )

        success = bool(res and res.success)

        if success and reset_traffic:
            await cls.reset_client_node_traffic(
                http_client, redis_client, node, user["email"]
            )

        return success

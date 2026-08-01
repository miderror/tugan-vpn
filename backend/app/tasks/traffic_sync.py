import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

from app.services.node import NodeService

logger = logging.getLogger(__name__)
db_engine = engine_finder()


async def _dispatch_nodes_operation(
    ctx: dict[str, Any],
    tg_id: int,
    node_action: Callable[..., Coroutine[Any, Any, bool]],
) -> None:
    http_client = ctx["http_client"]
    redis_client = ctx["redis"]

    user_rows = await db_engine.run_querystring(
        QueryString(
            """
            SELECT client_id, email, sub_id, expiry_date, is_active_vpn 
            FROM core_user 
            WHERE tg_id = {} 
            LIMIT 1
            """,
            tg_id,
        )
    )

    if not user_rows:
        return

    nodes = await db_engine.run_querystring(
        QueryString(
            """
            SELECT id, api_url, username, password, inbound_id 
            FROM core_node 
            WHERE is_active = true
            """
        )
    )

    if not nodes:
        return

    user_raw = user_rows[0]

    tasks = [
        node_action(
            http_client=http_client,
            redis_client=redis_client,
            node=node,
            user_data=user_raw,
        )
        for node in nodes
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for node, result in zip(nodes, results):
        if isinstance(result, Exception) or not result:
            logger.warning(
                "Failed node operation for user %d on node %d: %s",
                tg_id,
                node["id"],
                result,
            )


async def create_user_on_nodes_task(ctx: dict[str, Any], *, tg_id: int) -> None:
    await _dispatch_nodes_operation(
        ctx, tg_id=tg_id, node_action=NodeService.add_client_on_node
    )


async def update_user_on_nodes_task(ctx: dict[str, Any], *, tg_id: int) -> None:
    await _dispatch_nodes_operation(
        ctx, tg_id=tg_id, node_action=NodeService.update_client_on_node
    )

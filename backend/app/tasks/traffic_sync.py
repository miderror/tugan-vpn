import logging

import httpx
from piccolo.engine import engine_finder

from app.config.settings import settings
from app.services.node import NodeService

logger = logging.getLogger(__name__)
db_engine = engine_finder()


async def sync_all_active_nodes_traffic(ctx: dict) -> None:
    nodes = await db_engine.run_raw(
        "SELECT id, api_url, username, password, inbound_id, node_type FROM core_node WHERE is_active = TRUE"
    )
    if not nodes:
        return

    http_client: httpx.AsyncClient = ctx["http_client"]
    redis_client = ctx["redis"]

    updates_buffer: list[tuple[int, str]] = []

    for node in nodes:
        try:
            clients = await NodeService.fetch_node_traffics(
                http_client, redis_client, node
            )
            for c in clients:
                if not c.email:
                    continue
                bytes_used = c.up + c.down
                if bytes_used > 0:
                    updates_buffer.append((bytes_used, c.email))
        except Exception as e:
            logger.error("Error syncing traffic for node %d: %s", node["id"], e)
            continue

    if updates_buffer:
        chunk_size = 500
        for i in range(0, len(updates_buffer), chunk_size):
            chunk = updates_buffer[i : i + chunk_size]
            values_str = ", ".join(
                f"({b_added}::bigint, '{email}')" for b_added, email in chunk
            )

            await db_engine.run_raw(
                f"""
                UPDATE core_user AS u
                SET used_bytes = u.used_bytes + v.bytes_added,
                    updated_at = CURRENT_TIMESTAMP
                FROM (VALUES {values_str}) AS v(bytes_added, email)
                WHERE u.email = v.email
                """
            )

    expired_users = await db_engine.run_raw(
        """
        UPDATE core_user 
        SET is_active_vpn = FALSE 
        WHERE (used_bytes >= $1 OR expiry_date < CURRENT_TIMESTAMP) 
          AND is_active_vpn = TRUE
        RETURNING tg_id, client_id, email, sub_id, expiry_date, total_bytes
        """,
        settings.default_traffic_limit_bytes,
    )

    for u in expired_users:
        for node in nodes:
            await NodeService.upsert_and_reset_client_on_node(
                http_client, redis_client, node, u, enable=False, reset_traffic=False
            )

import asyncio

import httpx
from app.api.v1.auth import AuthController
from app.api.v1.billing import BillingController
from app.api.v1.users import UserController
from app.config.redis_client import init_redis_pool
from app.config.settings import settings
from app.db.tables import Node, Payment, Referral, Tariff, User
from app.tasks.traffic_sync import create_user_on_nodes_task, update_user_on_nodes_task
from litestar import Litestar, Response, Router, asgi
from litestar.exceptions import NotAuthorizedException, ValidationException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from litestar.types import Receive, Scope, Send
from piccolo.engine import engine_finder
from piccolo_admin.endpoints import create_admin
from saq import Queue, Worker

admin_asgi_app = create_admin(
    tables=[User, Referral, Node, Tariff, Payment],
    site_name="Tugan VPN Panel",
)


@asgi(path=settings.admin_path, is_mount=True, copy_scope=False)
async def admin_handler(scope: Scope, receive: Receive, send: Send) -> None:
    await admin_asgi_app(scope, receive, send)


api_v1_router = Router(
    path="/api/v1",
    route_handlers=[AuthController, UserController, BillingController],
)


async def open_services_connections(app: Litestar) -> None:
    engine = engine_finder()
    await engine.start_connection_pool(min_size=1, max_size=5)

    redis_client = await init_redis_pool()
    app.state.redis = redis_client
    app.state.settings = settings

    app.state.http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        timeout=httpx.Timeout(5.0, connect=3.0),
    )

    saq_queue = Queue.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
    )
    app.state.saq = saq_queue

    task_context = {
        "http_client": app.state.http_client,
        "redis": redis_client,
    }

    worker = Worker(
        queue=saq_queue,
        functions=[create_user_on_nodes_task, update_user_on_nodes_task],
        concurrency=2,
        startup=lambda ctx: ctx.update(task_context),
    )

    app.state.saq_worker_task = asyncio.create_task(worker.start())


async def close_services_connections(app: Litestar) -> None:
    if hasattr(app.state, "saq_worker_task"):
        app.state.saq_worker_task.cancel()
        try:
            await app.state.saq_worker_task
        except asyncio.CancelledError:
            pass

    if hasattr(app.state, "http_client"):
        await app.state.http_client.aclose()

    engine = engine_finder()
    await engine.close_connection_pool()

    if hasattr(app.state, "redis"):
        await app.state.redis.close()


def unauthorized_exception_handler(request, exception) -> Response:
    return Response(b"", status_code=HTTP_401_UNAUTHORIZED)


def validation_exception_request_handler(request, exception) -> Response:
    print("\n--- ОШИБКА ВАЛИДАЦИИ ВХОДЯЩИХ ДАННЫХ ---")
    print(exception.extra)
    print("----------------------------------------\n")

    return Response("validation err", status_code=HTTP_400_BAD_REQUEST)


def empty_bad_request_handler(request, exception) -> Response:
    return Response("test-hello", status_code=HTTP_400_BAD_REQUEST)


app = Litestar(
    route_handlers=[admin_handler, api_v1_router],
    debug=settings.debug,
    on_startup=[open_services_connections],
    on_shutdown=[close_services_connections],
    exception_handlers={
        NotAuthorizedException: unauthorized_exception_handler,
        ValidationException: validation_exception_request_handler,
        Exception: empty_bad_request_handler,
    },
)

from app.api.v1.auth import AuthController
from app.config.redis_client import init_redis_pool
from app.config.settings import settings
from app.db.tables import User
from litestar import Litestar, Response, Router, asgi
from litestar.exceptions import ValidationException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from litestar.types import Receive, Scope, Send
from piccolo.engine import engine_finder
from piccolo_admin.endpoints import create_admin

admin_asgi_app = create_admin(
    tables=[User],
    site_name="Tugan VPN Panel",
)


@asgi(path=settings.admin_path, is_mount=True, copy_scope=False)
async def admin_handler(scope: Scope, receive: Receive, send: Send) -> None:
    await admin_asgi_app(scope, receive, send)


api_v1_router = Router(
    path="/api/v1",
    route_handlers=[AuthController],
)


async def open_services_connections(app: Litestar) -> None:
    engine = engine_finder()
    await engine.start_connection_pool(min_size=1, max_size=5)

    app.state.redis = await init_redis_pool()
    app.state.settings = settings


async def close_services_connections() -> None:
    engine = engine_finder()
    await engine.close_connection_pool()

    if hasattr(app.state, "redis"):
        await app.state.redis.close()


def validation_exception_request_handler(request, exception) -> Response:
    print("\n--- ОШИБКА ВАЛИДАЦИИ ВХОДЯЩИХ ДАННЫХ ---")
    print(exception.extra)
    print("----------------------------------------\n")

    return Response("validation err", status_code=HTTP_400_BAD_REQUEST)


def empty_bad_request_handler(request, exception) -> Response:
    return Response("test-hello", status_code=HTTP_400_BAD_REQUEST)


app = Litestar(
    route_handlers=[admin_handler, api_v1_router],
    debug=True,
    on_startup=[open_services_connections],
    on_shutdown=[close_services_connections],
    exception_handlers={
        ValidationException: validation_exception_request_handler,
        Exception: empty_bad_request_handler,
    },
)

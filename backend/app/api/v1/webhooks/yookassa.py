import msgspec
from litestar import Controller, Request, Response, post
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

db_engine = engine_finder()


class YookassaAmount(msgspec.Struct, gc=False):
    value: str
    currency: str


class YookassaMetadata(msgspec.Struct, gc=False):
    user_id: str
    tariff_id: str


class YookassaPaymentObject(msgspec.Struct, gc=False):
    id: str
    status: str
    amount: YookassaAmount
    metadata: YookassaMetadata


class YookassaWebhookPayload(msgspec.Struct, gc=False):
    type: str
    event: str
    object: YookassaPaymentObject


YOOKASSA_DECODER = msgspec.json.Decoder(YookassaWebhookPayload)
OK_RESPONSE = Response(b"", media_type="application/json")


class YookassaWebhookController(Controller):
    path = "/api/yookassa"

    @post("/webhook/", status_code=HTTP_200_OK)
    async def handle_webhook(self, request: Request) -> Response:
        body = await request.body()
        try:
            payload = YOOKASSA_DECODER.decode(body)
        except msgspec.DecodeError:
            return Response(b"", status_code=HTTP_400_BAD_REQUEST)

        if payload.event != "payment.succeeded" or payload.object.status != "succeeded":
            return OK_RESPONSE

        try:
            payment_id = payload.object.id
            tg_id = int(payload.object.metadata.user_id)
            tariff_id = int(payload.object.metadata.tariff_id)
        except (ValueError, TypeError, AttributeError):
            return OK_RESPONSE

        db_result = await db_engine.run_querystring(
            QueryString(
                """
                SELECT success, amount_str, tariff_name, username 
                FROM process_yookassa_payment({}, {}, {})
                """,
                payment_id,
                tg_id,
                tariff_id,
            )
        )

        if not db_result or not db_result[0].get("success"):
            return OK_RESPONSE

        row = db_result[0]
        amount_str: str = row["amount_str"]
        tariff_name: str = row["tariff_name"]
        username: str = row["username"]

        saq_queue = getattr(request.app.state, "saq", None)
        if saq_queue:
            await saq_queue.enqueue("update_user_on_nodes_task", tg_id=tg_id)
            await saq_queue.enqueue(
                "send_payment_success_notification_task",
                user_id=tg_id,
                amount=amount_str,
                tariff_name=tariff_name,
            )
            await saq_queue.enqueue(
                "send_admin_payment_notification_task",
                user_id=tg_id,
                username=username,
                payment_id=payment_id,
                amount=amount_str,
                tariff_name=tariff_name,
            )

        return OK_RESPONSE

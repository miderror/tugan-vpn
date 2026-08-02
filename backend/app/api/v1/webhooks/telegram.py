import msgspec
from litestar import Controller, Request, Response, post
from litestar.status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED


class TelegramChat(msgspec.Struct, gc=False):
    id: int


class TelegramMessage(msgspec.Struct, gc=False):
    message_id: int
    chat: TelegramChat
    text: str = ""


class TelegramUpdate(msgspec.Struct, gc=False):
    update_id: int
    message: TelegramMessage | None = None


UPDATE_DECODER = msgspec.json.Decoder(TelegramUpdate)
OK_RESPONSE = Response(b"", status_code=HTTP_200_OK, media_type="application/json")


class TelegramWebhookController(Controller):
    path = "/api/telegram"

    @post("/webhook/", status_code=HTTP_200_OK)
    async def handle_webhook(self, request: Request) -> Response:
        settings = request.app.state.settings

        if settings.telegram_webhook_secret:
            secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret_header != settings.telegram_webhook_secret:
                return Response(b"", status_code=HTTP_401_UNAUTHORIZED)

        body = await request.body()
        try:
            update = UPDATE_DECODER.decode(body)
        except msgspec.DecodeError:
            return OK_RESPONSE

        if update.message and update.message.text.startswith("/start"):
            saq_queue = getattr(request.app.state, "saq", None)
            if saq_queue:
                await saq_queue.enqueue(
                    "send_bot_start_message_task",
                    chat_id=update.message.chat.id,
                )

        return OK_RESPONSE

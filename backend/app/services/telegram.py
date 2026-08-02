import httpx
import msgspec

from app.config.settings import settings

TG_SEND_MESSAGE_URL = (
    f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
)


class InlineKeyboardButton(msgspec.Struct, gc=False):
    text: str
    url: str


class InlineKeyboardMarkup(msgspec.Struct, gc=False):
    inline_keyboard: list[list[InlineKeyboardButton]]


class TelegramMessagePayload(msgspec.Struct, gc=False):
    chat_id: int
    text: str
    parse_mode: str = "HTML"
    reply_markup: InlineKeyboardMarkup | None = None


PAYLOAD_ENCODER = msgspec.json.Encoder()


def _pluralize(n: int, single: str, few: str, many: str) -> str:
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return f"{n} {single}"
    if 2 <= n10 <= 4 and (n100 < 10 or n100 >= 20):
        return f"{n} {few}"
    return f"{n} {many}"


async def send_telegram_message(
    http_client: httpx.AsyncClient,
    chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> bool:
    payload = TelegramMessagePayload(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
    )

    try:
        resp = await http_client.post(
            TG_SEND_MESSAGE_URL,
            content=PAYLOAD_ENCODER.encode(payload),
            headers={"Content-Type": "application/json"},
            timeout=4.0,
        )
        return resp.status_code == 200
    except httpx.HTTPError:
        return False

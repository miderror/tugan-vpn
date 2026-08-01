import uuid
from typing import Any, ClassVar

import httpx
import msgspec
from litestar import Controller, Request, Response, get, post
from litestar.di import Provide
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

from app.services.auth import provide_authenticated_tg_id

db_engine = engine_finder()


class CreatePaymentRequest(msgspec.Struct, gc=False):
    tariff_id: int = msgspec.field(name="tid")
    email: str = msgspec.field(name="em")


class PaymentResponse(msgspec.Struct, gc=False):
    payment_url: str = msgspec.field(name="url")


class TariffItem(msgspec.Struct, gc=False):
    id: int
    display_name: str = msgspec.field(name="dn")
    duration_days: int = msgspec.field(name="dd")
    price: str = msgspec.field(name="p")
    is_bestseller: bool = msgspec.field(name="ib")
    original_price: str | None = msgspec.field(name="op")


RESPONSE_ENCODER = msgspec.json.Encoder()


def _validate_email(email: str) -> bool:
    if not (5 <= len(email) <= 254):
        return False
    at_idx = email.find("@")
    return at_idx > 0 and email.find(".", at_idx) > at_idx + 1


class BillingController(Controller):
    path = "/billing"
    dependencies: ClassVar[dict[str, Any]] = {
        "tg_id": Provide(provide_authenticated_tg_id)
    }

    @get("/tariffs", status_code=HTTP_200_OK)
    async def get_tariffs(self) -> Response:
        rows = await db_engine.run_querystring(
            QueryString(
                """
                SELECT id, display_name, duration_days, 
                       price::text, is_bestseller, original_price::text 
                FROM core_tariff 
                WHERE is_active = true 
                ORDER BY duration_days ASC
                """
            )
        )
        items = [
            TariffItem(
                id=r["id"],
                display_name=r["display_name"],
                duration_days=r["duration_days"],
                price=r["price"],
                is_bestseller=r["is_bestseller"],
                original_price=r["original_price"],
            )
            for r in rows
        ]
        return Response(RESPONSE_ENCODER.encode(items), media_type="application/json")

    @post("/create_payment", status_code=HTTP_200_OK)
    async def create_payment(
        self, request: Request, tg_id: int, data: CreatePaymentRequest
    ) -> Response:
        if not data.tariff_id or not data.email or not _validate_email(data.email):
            return Response(b"", status_code=HTTP_400_BAD_REQUEST)

        rows = await db_engine.run_querystring(
            QueryString(
                """
                SELECT t.price::text, t.display_name, u.first_name, u.last_name
                FROM core_tariff t
                JOIN core_user u ON u.tg_id = {}
                WHERE t.id = {} AND t.is_active = true
                LIMIT 1
                """,
                tg_id,
                data.tariff_id,
            )
        )

        if not rows:
            return Response(b"", status_code=HTTP_400_BAD_REQUEST)

        row = rows[0]
        price_str = row["price"]
        first_name = row.get("first_name") or ""
        last_name = row.get("last_name") or ""
        customer_name = f"{first_name} {last_name}".strip() or "Telegram User"

        settings = request.app.state.settings
        http_client = request.app.state.http_client

        payload = {
            "amount": {"value": price_str, "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": settings.webapp_url,
            },
            "capture": True,
            "description": f"Оплата подписки на {row['display_name']}",
            "metadata": {
                "user_id": str(tg_id),
                "tariff_id": str(data.tariff_id),
            },
            "receipt": {
                "customer": {
                    "full_name": customer_name,
                    "email": data.email,
                    "phone": "+79000000000",
                },
                "tax_system_code": 1,
                "items": [
                    {
                        "description": "Пополнение баланса",
                        "quantity": "1.00",
                        "amount": {"value": price_str, "currency": "RUB"},
                        "vat_code": 6,
                        "payment_subject": "service",
                        "payment_mode": "full_prepayment",
                    }
                ],
            },
        }

        try:
            resp = await http_client.post(
                "https://api.yookassa.ru/v3/payments",
                content=RESPONSE_ENCODER.encode(payload),
                headers={
                    "Authorization": settings.yookassa_auth_header,
                    "Idempotence-Key": str(uuid.uuid4()),
                    "Content-Type": "application/json",
                },
                timeout=5.0,
            )

            if resp.status_code != 200:
                return Response(b"", status_code=HTTP_500_INTERNAL_SERVER_ERROR)

            resp_data = msgspec.json.decode(resp.content)
            confirmation_url = resp_data["confirmation"]["confirmation_url"]

            return Response(
                RESPONSE_ENCODER.encode(PaymentResponse(payment_url=confirmation_url)),
                media_type="application/json",
            )
        except (httpx.HTTPError, msgspec.DecodeError, KeyError):
            return Response(b"", status_code=HTTP_500_INTERNAL_SERVER_ERROR)

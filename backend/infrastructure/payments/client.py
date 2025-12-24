import logging
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from django.conf import settings
from yookassa import Configuration, Payment

logger = logging.getLogger("infrastructure.payments")


class PaymentError(Exception):
    pass


class YookassaAdapter:
    def __init__(self):
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    def create_payment(
        self,
        amount: Decimal,
        description: str,
        return_url: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        try:
            idempotence_key = str(uuid.uuid4())
            payment = Payment.create(
                {
                    "amount": {"value": str(amount), "currency": "RUB"},
                    "confirmation": {"type": "redirect", "return_url": return_url},
                    "capture": True,
                    "description": description,
                    "metadata": metadata or {},
                },
                idempotence_key,
            )

            return {
                "provider_id": payment.id,
                "status": payment.status,
                "url": payment.confirmation.confirmation_url,
            }
        except Exception as e:
            logger.error(f"Yookassa create error: {e}")
            raise PaymentError(str(e))

    def check_status(self, provider_id: str) -> str:
        try:
            payment = Payment.find_one(provider_id)
            return payment.status
        except Exception as e:
            logger.error(f"Yookassa check error: {e}")
            raise PaymentError(str(e))

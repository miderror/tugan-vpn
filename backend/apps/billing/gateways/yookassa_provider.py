import logging
import uuid
from decimal import Decimal
from typing import Dict, Optional

from django.conf import settings
from yookassa import Configuration
from yookassa import Payment as YookassaSDK
from yookassa.domain.common import PaymentStatus as YookassaStatus
from yookassa.domain.notification import WebhookNotificationFactory

from apps.billing.models import Payment

from .base import BaseGateway, GatewayError, PaymentDTO

logger = logging.getLogger(__name__)

YookassaStatus.PENDING


class YookassaGateway(BaseGateway):
    def __init__(self):
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    def _validate_status(self, provider_status: str) -> str:
        if provider_status in Payment.Status.values:
            return provider_status

        logger.warning(f"Unknown status from Yookassa: {provider_status}")
        return Payment.Status.PENDING

    def create_payment(
        self,
        amount: Decimal,
        currency: str,
        return_url: str,
        description: str,
        user_id: int,
        email: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> PaymentDTO:
        try:
            idempotence_key = str(uuid.uuid4())
            payload = {
                "amount": {"value": str(amount), "currency": currency},
                "confirmation": {"type": "redirect", "return_url": return_url},
                "capture": True,
                "description": description,
                "metadata": metadata or {},
                "receipt": {
                    "customer": {"email": email} if email else {},
                    "items": [
                        {
                            "description": description,
                            "quantity": "1.00",
                            "amount": {"value": str(amount), "currency": currency},
                            "vat_code": 6,
                            "payment_subject": "service",
                            "payment_mode": "full_prepayment",
                        }
                    ],
                },
            }

            if not email:
                del payload["receipt"]

            payment = YookassaSDK.create(payload, idempotence_key)

            return PaymentDTO(
                external_id=payment.id,
                payment_url=payment.confirmation.confirmation_url,
                status=self._validate_status(payment.status),
                raw_response=dict(payment),
            )
        except Exception as e:
            logger.error(f"Yookassa create error: {e}", exc_info=True)
            raise GatewayError(f"Provider error: {str(e)}")

    def check_payment_status(self, external_id: str) -> str:
        try:
            payment = YookassaSDK.find_one(external_id)
            return self._validate_status(payment.status)
        except Exception as e:
            logger.error(f"Yookassa check status error: {e}")
            raise GatewayError(f"Check status error: {str(e)}")

    def parse_webhook(self, request_body: bytes, headers: Dict) -> Dict:
        try:
            notification_object = WebhookNotificationFactory().create(
                request_body.decode("utf-8")
            )
            response_object = notification_object.object
            return {
                "external_id": response_object.id,
                "status": response_object.status,
                "raw": dict(response_object),
            }
        except Exception as e:
            logger.error(f"Webhook parsing failed: {e}")
            raise GatewayError("Invalid webhook data")

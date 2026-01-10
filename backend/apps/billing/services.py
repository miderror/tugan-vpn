import logging

from core.event_bus.publisher import publish
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.access.models import Tariff
from apps.users.models import User

from .events import PaymentSucceeded
from .gateways import GatewayError, PaymentGatewayFactory
from .models import Payment

logger = logging.getLogger(__name__)


class BillingService:
    @staticmethod
    def initiate_payment(
        user: User, tariff_id: int, gateway_name: str, email: str
    ) -> str:
        try:
            tariff = Tariff.objects.get(id=tariff_id, is_active=True)
        except Tariff.DoesNotExist:
            raise ValueError("Invalid or inactive tariff")

        gateway = PaymentGatewayFactory.get_gateway(gateway_name)

        with transaction.atomic():
            payment = Payment.objects.create(
                user=user,
                tariff=tariff,
                amount=tariff.price,
                currency="RUB",
                gateway=gateway_name,
                receipt_email=email,
                status=Payment.Status.PENDING,
            )

            try:
                dto = gateway.create_payment(
                    amount=float(tariff.price),
                    currency="RUB",
                    return_url=settings.WEBAPP_URL,
                    description=f"Оплата подписки на {tariff.display_name}",
                    user_id=user.telegram_id,
                    email=email,
                    metadata={"payment_id": str(payment.id)},
                )
            except GatewayError as e:
                payment.status = Payment.Status.FAILED
                payment.provider_payload = {"error": str(e)}
                payment.save(update_fields=["status", "provider_payload"])
                raise e

            payment.external_id = dto.external_id
            payment.provider_payload = dto.raw_response
            payment.save(update_fields=["external_id", "provider_payload"])

            return dto.payment_url

    @staticmethod
    @transaction.atomic
    def process_webhook(gateway_name: str, body: bytes, headers: dict):
        gateway = PaymentGatewayFactory.get_gateway(gateway_name)

        try:
            data = gateway.parse_webhook(body, headers)
        except GatewayError:
            return

        external_id = data["external_id"]

        current_status = (
            Payment.objects.filter(external_id=external_id)
            .values_list("status", flat=True)
            .first()
        )

        if not current_status:
            logger.warning(f"Webhook ignore: unknown payment {external_id}")
            return

        if current_status == Payment.Status.SUCCEEDED:
            return

        try:
            verified_status = gateway.check_payment_status(external_id)
        except GatewayError:
            logger.error(f"Verification failed for {external_id}")
            return

        with transaction.atomic():
            try:
                payment = (
                    Payment.objects.select_for_update()
                    .select_related("tariff", "user")
                    .get(external_id=external_id)
                )
            except Payment.DoesNotExist:
                return

            if payment.status == Payment.Status.SUCCEEDED:
                return

            payment.status = verified_status
            payment.provider_payload = data.get("raw", {})

            if verified_status != Payment.Status.SUCCEEDED:
                payment.save(update_fields=["status", "provider_payload", "updated_at"])
                return

            payment.completed_at = timezone.now()
            payment.save(
                update_fields=[
                    "status",
                    "provider_payload",
                    "updated_at",
                    "completed_at",
                ]
            )

            logger.info(
                f"Revenue: {payment.amount} {payment.currency}. User: {payment.user_id}"
            )

            event = PaymentSucceeded(
                user_id=payment.user.telegram_id,
                amount=float(payment.amount),
                currency=payment.currency,
                tariff_days=payment.tariff.duration_days,
                tariff_name=payment.tariff.display_name,
                payment_id=str(payment.id),
            )
            publish(event)

            logger.info(f"Payment processed: {payment.id}")

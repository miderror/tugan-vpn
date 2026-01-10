import logging

from core.event_bus.decorators import subscribe

from apps.billing.events import PaymentSucceeded

from .services.subscription import SubscriptionService

logger = logging.getLogger(__name__)


@subscribe(PaymentSucceeded)
def on_payment_succeeded_access(event: PaymentSucceeded):
    logger.info(f"Granting access for user {event.user_id}, days: {event.tariff_days}")

    SubscriptionService.extend_subscriptions(
        days=event.tariff_days, mode="user", user_ids=[event.user_id]
    )

from core.event_bus.decorators import subscribe

from apps.billing.events import PaymentSucceeded

from .services.dispatcher import NotificationDispatcher


@subscribe(PaymentSucceeded)
def on_payment_succeeded_notify(event: PaymentSucceeded):
    message = (
        f"✅ Оплата {event.amount} {event.currency} прошла успешно!\n"
        f"Подписка продлена на: {event.tariff_name}."
    )
    NotificationDispatcher().send_transactional(event.user_id, message)

from core.event_bus.base import IntegrationEvent


class PaymentSucceeded(IntegrationEvent):
    user_id: int
    amount: float
    currency: str
    tariff_days: int
    tariff_name: str
    payment_id: str

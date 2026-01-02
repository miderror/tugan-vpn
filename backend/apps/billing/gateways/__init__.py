from .base import BaseGateway
from .yookassa_provider import YookassaGateway


class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(gateway_name: str) -> BaseGateway:
        if gateway_name == "yookassa":
            return YookassaGateway()
        raise ValueError(f"Unknown gateway: {gateway_name}")

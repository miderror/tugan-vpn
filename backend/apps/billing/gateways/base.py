from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PaymentDTO:
    external_id: str
    payment_url: str
    status: str
    raw_response: Dict[str, Any]


class GatewayError(Exception):
    pass


class BaseGateway(ABC):
    @abstractmethod
    def create_payment(
        self,
        amount: float,
        currency: str,
        return_url: str,
        description: str,
        user_id: int,
        email: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> PaymentDTO:
        pass

    @abstractmethod
    def check_payment_status(self, external_id: str) -> str:
        pass

    @abstractmethod
    def parse_webhook(self, request_body: bytes, headers: Dict) -> Dict:
        pass

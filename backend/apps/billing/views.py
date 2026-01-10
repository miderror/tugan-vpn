import logging

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponseServerError
from rest_framework.views import APIView

from .gateways import GatewayError
from .services import BillingService

logger = logging.getLogger(__name__)


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tariff_id = request.data.get("tariff_id")
        email = request.data.get("email")
        gateway = request.data.get("gateway", "yookassa")

        if not tariff_id or not email:
            raise ValidationError("tariff_id and email are required")

        try:
            payment_url = BillingService.initiate_payment(
                user=request.user,
                tariff_id=tariff_id,
                gateway_name=gateway,
                email=email,
            )
            return Response(
                {"payment_url": payment_url}, status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except GatewayError as e:
            logger.error(f"Gateway error: {e}")
            return Response(
                {"detail": "Payment provider error"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            logger.exception(f"Critical billing error: {e}")
            return Response(
                {"detail": "Internal error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class YookassaWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            BillingService.process_webhook(
                gateway_name="yookassa", body=request.body, headers=request.headers
            )
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}", exc_info=True)

        return Response(status=status.HTTP_200_OK)

from django.urls import path

from .views import CreatePaymentView, YookassaWebhookView

urlpatterns = [
    path("payment/create/", CreatePaymentView.as_view(), name="payment-create"),
    path("webhooks/yookassa/", YookassaWebhookView.as_view(), name="webhook-yookassa"),
]

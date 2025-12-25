from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubscriptionFileView, TariffViewSet, VpnViewSet

router = DefaultRouter()
router.register(r"tariffs", TariffViewSet, basename="tariff")
router.register(r"vpn", VpnViewSet, basename="vpn")

urlpatterns = [
    path("", include(router.urls)),
    path("sub/<str:token>/", SubscriptionFileView.as_view(), name="subscription-file"),
]

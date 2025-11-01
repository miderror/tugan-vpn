from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TariffViewSet

router = DefaultRouter()
router.register(r"tariffs", TariffViewSet, basename="tariff")

urlpatterns = [
    path("", include(router.urls)),
]

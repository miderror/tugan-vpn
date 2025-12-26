from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReferralViewSet

router = DefaultRouter()
router.register(r"referrals", ReferralViewSet, basename="referrals")

urlpatterns = [
    path("", include(router.urls)),
]

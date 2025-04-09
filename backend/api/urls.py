from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ReferralViewSet, TariffViewSet,
)
from ninja import NinjaAPI
from .ninja_api.xui import router as xui_router
from .ninja_api.yookassa import router as yookassa_router
from .ninja_api.root_router import router as root_router

ninja_api = NinjaAPI()
ninja_api.add_router("yookassa", yookassa_router)
ninja_api.add_router("xui", xui_router)
ninja_api.add_router("", root_router)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'referrals', ReferralViewSet)
router.register(r'tariffs', TariffViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', ninja_api.urls),
]

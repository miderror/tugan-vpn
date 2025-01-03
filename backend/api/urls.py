from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ConnectionViewSet, PaymentViewSet, KeyViewSet,
    ReferralViewSet, CouponViewSet, CouponUsageViewSet, NotificationViewSet
)


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'connections', ConnectionViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'keys', KeyViewSet)
router.register(r'referrals', ReferralViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'coupon-usages', CouponUsageViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

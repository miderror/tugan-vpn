from rest_framework import viewsets
from .models import User, Connection, Payment, Key, Referral, Coupon, CouponUsage, Notification
from .serializers import (
    UserSerializer, ConnectionSerializer, PaymentSerializer, KeySerializer,
    ReferralSerializer, CouponSerializer, CouponUsageSerializer, NotificationSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class KeyViewSet(viewsets.ModelViewSet):
    queryset = Key.objects.all()
    serializer_class = KeySerializer


class ReferralViewSet(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer


class CouponUsageViewSet(viewsets.ModelViewSet):
    queryset = CouponUsage.objects.all()
    serializer_class = CouponUsageSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

from django.contrib import admin
from .models import (
    User, Connection, Payment, Key, Referral, Coupon, CouponUsage, Notification, Tariff
)

admin.site.register(User)
admin.site.register(Connection)
admin.site.register(Payment)
admin.site.register(Key)
admin.site.register(Referral)
admin.site.register(Coupon)
admin.site.register(CouponUsage)
admin.site.register(Notification)
admin.site.register(Tariff)

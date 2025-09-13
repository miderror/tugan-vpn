from django.contrib import admin
from .models import (
    User, Connection, Payment, Key, Referral, Coupon, CouponUsage, Notification, Tariff
)

class UserAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'username', 'first_name', 'last_name', 'created_at')
    search_fields = ('tg_id', 'username', 'first_name', 'last_name')

class KeyAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'email', 'access_token', 'expiry_date', 'total_gb', 'used_gb', 'is_active', 'can_claim_gift'
    )
    search_fields = ('user__tg_id', 'user__username', 'email', 'access_token')
    list_filter = ('is_active', 'can_claim_gift')
    raw_id_fields = ('user',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_system', 'status', 'payment_id', 'created_at')
    search_fields = ('user__tg_id', 'user__username', 'payment_id')
    list_filter = ('status', 'payment_system')
    raw_id_fields = ('user',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'notification_type', 'last_notification_time')
    search_fields = ('tg_id', 'notification_type')
    list_filter = ('notification_type',)

admin.site.register(User, UserAdmin)
admin.site.register(Connection)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(Referral)
admin.site.register(Coupon)
admin.site.register(CouponUsage)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Tariff)

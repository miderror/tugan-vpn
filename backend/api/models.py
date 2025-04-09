from datetime import datetime
import uuid
from django.db import models


class User(models.Model):
    tg_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    utm_source = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"User {self.tg_id} ({self.username})"


class Connection(models.Model):
    tg_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    balance = models.FloatField(default=0.0)
    trial = models.IntegerField(default=0)

    def __str__(self):
        return f"Connection for {self.tg_id.username}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_system = models.CharField(max_length=255)
    status = models.CharField(default='success', max_length=255)
    payment_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for {self.user.username} ({self.user.username})"


class Key(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.BigIntegerField()
    sub_id = models.CharField(max_length=255, unique=True)
    total_bytes = models.BigIntegerField(default=107374182400)
    used_bytes = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    access_token = models.CharField(max_length=255, unique=True)
    can_claim_gift = models.BooleanField(default=True)
    tried_to_connect = models.BooleanField(default=False)
    next_reset_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Key for {self.user.tg_id} ({self.user.username})"
    
    @property
    def total_gb(self):
        value = self.total_bytes / (1024 ** 3)
        return f"{value:.1f}"

    @property
    def used_gb(self):
        value = self.used_bytes / (1024 ** 3)
        return f"{value:.1f}"

    @property
    def expiry_date(self):
        return datetime.fromtimestamp(self.expiry_time / 1000).strftime("%d.%m.%Y")


class Referral(models.Model):
    referred_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='referred_tg_user'
    )
    referrer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='referrer_tg_user'
    )
    reward_issued = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Referral {self.referred_user.tg_id} by {self.referrer_user.tg_id} "
            f"({self.referred_user.username} by {self.referrer_user.username})"
        )

class Coupon(models.Model):
    code = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()
    usage_limit = models.IntegerField(default=1)
    usage_count = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Coupon {self.code}"


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    used_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Coupon {self.coupon.code} used by {self.user_id}"


class Notification(models.Model):
    tg_id = models.BigIntegerField()
    last_notification_time = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=255)

    class Meta:
        unique_together = ('tg_id', 'notification_type')

    def __str__(self):
        return f"Notification for {self.tg_id} - {self.notification_type}"

class Tariff(models.Model):
    duration = models.CharField(max_length=50)
    price = models.FloatField()
    total = models.FloatField()
    original_price = models.FloatField(null=True, blank=True)
    is_bestseller = models.BooleanField(default=False)
    period_days = models.IntegerField()

    def __str__(self):
        return f"Tariff {self.duration} (₽{self.total})"

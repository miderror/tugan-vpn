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

    def __str__(self):
        return f"User {self.tg_id}"


class Connection(models.Model):
    tg_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    balance = models.FloatField(default=0.0)
    trial = models.IntegerField(default=0)

    def __str__(self):
        return f"Connection for {self.tg_id.username}"


class Payment(models.Model):
    tg_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_system = models.CharField(max_length=255)
    status = models.CharField(default='success', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for {self.tg_id.username}"


class Key(models.Model):
    tg_id = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.BigIntegerField()
    expiry_time = models.BigIntegerField()
    key = models.TextField()
    server_id = models.CharField(max_length=255, default='cluster1')
    notified = models.BooleanField(default=False)
    notified_24h = models.BooleanField(default=False)

    def __str__(self):
        return f"Key for {self.tg_id.username}"


class Referral(models.Model):
    referred_tg_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='referred_user'
    )
    referrer_tg_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='referrer_user'
    )
    reward_issued = models.BooleanField(default=False)

    def __str__(self):
        return f"Referral {self.referred_tg_id.tg_id} by {self.referrer_tg_id.tg_id}"

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

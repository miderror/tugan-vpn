import uuid

from django.db import models


class User(models.Model):
    tg_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)

    utm_source = models.CharField(max_length=64, null=True, blank=True)
    referrer = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        db_index=True,
    )

    email = models.CharField(max_length=255, unique=True, db_index=True)
    sub_id = models.UUIDField(default=uuid.uuid4, unique=True)

    total_bytes = models.BigIntegerField(default=268435456000)
    used_bytes = models.BigIntegerField(default=0)

    is_active_vpn = models.BooleanField(default=False, db_index=True)
    can_claim_gift = models.BooleanField(default=True)

    expiry_date = models.DateTimeField(null=True, blank=True, db_index=True)
    next_traffic_reset = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tg_id} - {self.username}"

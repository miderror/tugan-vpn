from rest_framework import serializers

from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    usage = serializers.SerializerMethodField()
    subscription_date = serializers.SerializerMethodField()
    can_claim_gift = serializers.SerializerMethodField()
    ip = serializers.SerializerMethodField()
    vpn_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "telegram_id",
            "usage",
            "subscription_date",
            "can_claim_gift",
            "ip",
            "vpn_url",
        )

    def get_usage(self, obj):
        sub = getattr(obj, "subscription", None)
        if not sub:
            return "0 / 0 GB"
        return f"{sub.used_gb} / {sub.total_gb_limit} GB"

    def get_subscription_date(self, obj):
        sub = getattr(obj, "subscription", None)
        if not sub or not sub.is_active:
            return "Не активна"
        return sub.end_date.strftime("%d.%m.%Y")

    def get_can_claim_gift(self, obj):
        sub = getattr(obj, "subscription", None)
        return not sub.trial_activated if sub else True

    def get_ip(self, obj):
        request = self.context.get("request")
        if request:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                return x_forwarded_for.split(",")[0].strip()

        return "Unknown"

    def get_vpn_url(self, obj):
        sub = getattr(obj, "subscription", None)
        if sub:
            return sub.vless_link
        return ""

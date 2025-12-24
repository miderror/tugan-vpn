from django.contrib import admin

from .models import ReferralReward


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referral", "bonus_days_awarded", "awarded_at")
    list_filter = ("awarded_at",)
    search_fields = (
        "referrer__username",
        "referrer__telegram_id",
        "referral__username",
        "referral__telegram_id",
    )
    raw_id_fields = ("referrer", "referral")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

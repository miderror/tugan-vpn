from django.contrib import admin

from .models import Subscription, Tariff, VpnServer


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "duration_days",
        "price",
        "is_active",
        "order",
        "is_bestseller",
    )
    list_editable = ("is_active", "order", "price", "is_bestseller")
    list_filter = ("is_active",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "end_date",
        "is_active",
        "trial_activated",
        "used_gb_formatted",
        "total_gb_limit_formatted",
    )
    search_fields = ("user__telegram_id", "user__username")
    list_filter = ("end_date", "trial_activated", "is_vpn_client_active")
    readonly_fields = ("vless_uuid", "used_bytes", "last_traffic_update")
    raw_id_fields = ("user",)

    @admin.display(boolean=True, description="Активна")
    def is_active(self, obj):
        return obj.is_active

    @admin.display(description="Использовано ГБ")
    def used_gb_formatted(self, obj):
        return obj.used_gb

    @admin.display(description="Лимит ГБ")
    def total_gb_limit_formatted(self, obj):
        return obj.total_gb_limit


@admin.register(VpnServer)
class VpnServerAdmin(admin.ModelAdmin):
    list_display = ("name", "api_url", "inbound_id", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)

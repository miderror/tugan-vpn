from django.contrib import admin, messages
from django.shortcuts import redirect, render

from .forms import SubscriptionManagementForm
from .models import Subscription, SubscriptionManagement, Tariff, VpnServer


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "duration_days",
        "price",
        "is_active",
        "order",
        "is_bestseller",
    )
    list_editable = ("is_active", "order", "is_bestseller")
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
    list_display = ("name", "api_url_display", "inbound_id", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("name",)

    def api_url_display(self, obj):
        return obj.credentials.get("api_url", "-")

    api_url_display.short_description = "API URL"


@admin.register(SubscriptionManagement)
class SubscriptionManagementAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST":
            form = SubscriptionManagementForm(request.POST)
            if form.is_valid():
                self.message_user(
                    request,
                    "Функционал временно отключен для рефакторинга.",
                    messages.WARNING,
                )
                return redirect(request.path)
        else:
            form = SubscriptionManagementForm()

        context = {
            **self.admin_site.each_context(request),
            "title": "Subscription Management",
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/vpn/subscription_management.html", context)

from django.contrib import admin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "first_name",
        "referred_by",
        "date_joined",
    )
    search_fields = ("telegram_id", "username", "first_name")
    list_filter = ("date_joined",)
    raw_id_fields = ("referred_by",)
    readonly_fields = ("date_joined", "avatar_preview", "avatar_updated_at")

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "telegram_id",
                    "username",
                    "first_name",
                    "last_name",
                    "language_code",
                )
            },
        ),
        (
            "Аватар",
            {
                "fields": (
                    "avatar",
                    "avatar_preview",
                    "avatar_updated_at",
                )
            },
        ),
        ("Маркетинг", {"fields": ("utm_source", "referred_by")}),
        ("Служебное", {"fields": ("date_joined",)}),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 150px; border-radius: 10px;" />',
                obj.avatar.url,
            )
        return "Аватар не загружен"

    avatar_preview.short_description = "Предпросмотр"

    def has_add_permission(self, request):
        return False

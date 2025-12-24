from django.apps import AppConfig


class VpnConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vpn"

    def ready(self):
        import apps.vpn.signals  # noqa: F401

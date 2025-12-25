import hashlib
import secrets
import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_jsonform.models.fields import JSONField

SERVER_CREDENTIALS_SCHEMA = {
    "type": "dict",
    "keys": {
        "api_url": {
            "type": "string",
            "title": "API URL (3X-UI)",
            "required": True,
            "help": "Пример: http://1.2.3.4:2053",
        },
        "username": {
            "type": "string",
            "title": "Логин",
            "required": True,
        },
        "password": {
            "type": "string",
            "title": "Пароль",
            "required": True,
        },
    },
}


class Tariff(models.Model):
    display_name = models.CharField(
        max_length=100,
        verbose_name="Название для фронтенда",
        help_text="Например: 1 месяц",
    )
    duration_days = models.PositiveIntegerField(verbose_name="Длительность (дни)")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена (руб)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_bestseller = models.BooleanField(default=False, verbose_name="Бестселлер")
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старая цена (зачеркнутая)",
    )

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        ordering = ["order"]


class Subscription(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Пользователь",
    )
    end_date = models.DateTimeField(verbose_name="Дата окончания")

    email = models.CharField(max_length=255, unique=True, editable=False)
    sub_id = models.CharField(max_length=255, unique=True, editable=False)
    access_token = models.CharField(
        max_length=255, unique=True, editable=False, db_index=True
    )
    vless_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    trial_activated = models.BooleanField(
        default=False, verbose_name="Нажал кнопку с подарком"
    )

    has_ever_connected = models.BooleanField(
        default=False, verbose_name="Пытался подключиться хотя бы раз"
    )

    is_vpn_client_active = models.BooleanField(
        default=False, verbose_name="Клиент VPN активен в 3x-ui"
    )

    total_bytes_limit = models.BigIntegerField(
        default=268435456000, verbose_name="Лимит трафика (байты)"
    )
    used_bytes = models.BigIntegerField(
        default=0, verbose_name="Использовано трафика (байты)"
    )
    last_traffic_update = models.DateTimeField(
        null=True, blank=True, verbose_name="Последнее обновление трафика"
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.email = self._generate_unique_email()
            self.sub_id = self._generate_secure_sub_id()
            self.access_token = self._generate_access_token()
        super().save(*args, **kwargs)

    def _generate_unique_email(self):
        return f"{self.user.telegram_id}_{uuid.uuid4().hex}"

    def _generate_secure_sub_id(self):
        return f"{self.user.telegram_id}-{secrets.token_urlsafe(16)}"

    def _generate_access_token(self):
        unique_data = f"{self.user.telegram_id}{secrets.token_hex(16)}{timezone.now().timestamp()}"
        return hashlib.sha256(unique_data.encode()).hexdigest()

    def get_subscription_url(self):
        return reverse("subscription-file", args=[self.access_token])

    @property
    def vless_link(self):
        return self.get_subscription_url()

    @property
    def is_active(self):
        return self.end_date > timezone.now()

    @property
    def used_gb(self):
        return round(self.used_bytes / (1024**3), 2)

    @property
    def total_gb_limit(self):
        return round(self.total_bytes_limit / (1024**3), 2)

    def __str__(self):
        return f"Подписка для {self.user}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class VpnServer(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название сервера (для админки)"
    )
    credentials = JSONField(
        "Доступы к API",
        schema=SERVER_CREDENTIALS_SCHEMA,
        help_text="Настройки подключения к панели 3x-ui",
    )

    inbound_id = models.PositiveIntegerField(
        default=1, verbose_name="ID входящего подключения"
    )

    config_template = models.TextField(
        verbose_name="Шаблон конфига подключения",
        help_text=(
            "Вставить полный конфиг для подключения, заменив UUID клиента на {uuid}.<br>"
            "Пример: vless://{uuid}@1.2.3.4:443?type=tcp&...#NAME"
        ),
    )
    is_active = models.BooleanField(default=True, verbose_name="Сервер активен")

    def __str__(self):
        return self.name

    @property
    def api_url(self):
        return self.credentials.get("api_url")

    @property
    def api_username(self):
        return self.credentials.get("username")

    @property
    def api_password(self):
        return self.credentials.get("password")

    class Meta:
        verbose_name = "VPN Сервер"
        verbose_name_plural = "VPN Серверы"

import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from backend.users.models import User


class Tariff(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название тарифа (для админки)"
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
        return f"{self.name} ({self.duration_days} дней за {self.price} руб)"

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        ordering = ["order"]


class Subscription(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Пользователь",
    )
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    vless_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    trial_activated = models.BooleanField(
        default=False, verbose_name="Триал активирован"
    )

    total_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Всего пополнено"
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

    @property
    def is_active(self):
        return self.end_date > timezone.now()

    @property
    def used_gb(self):
        return round(self.used_bytes / (1024**3), 2)

    @property
    def total_gb_limit(self):
        return round(self.total_bytes_limit / (1024**3), 2)

    def extend_subscription(self, days: int):
        if self.end_date < timezone.now():
            self.end_date = timezone.now()
        self.end_date += timedelta(days=days)
        self.save()

    def __str__(self):
        return f"Подписка для {self.user}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class VpnServer(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название сервера (для админки)"
    )
    api_url = models.URLField(
        verbose_name="URL API 3x-ui", help_text="Пример: http://your_server_ip:2053"
    )
    api_username = models.CharField(max_length=100, verbose_name="Логин API")
    api_password = models.CharField(max_length=100, verbose_name="Пароль API")
    inbound_id = models.PositiveIntegerField(
        default=1, verbose_name="ID входящего подключения"
    )
    is_active = models.BooleanField(default=True, verbose_name="Сервер активен")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "VPN Сервер"
        verbose_name_plural = "VPN Серверы"

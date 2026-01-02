import uuid

from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        WAITING_FOR_CAPTURE = "waiting_for_capture", "Ожидает подтверждения"
        SUCCEEDED = "succeeded", "Успешно"
        CANCELED = "canceled", "Отменен"
        FAILED = "failed", "Ошибка"

    class Gateway(models.TextChoices):
        YOOKASSA = "yookassa", "Yookassa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    tariff = models.ForeignKey(
        "access.Tariff", on_delete=models.SET_NULL, null=True, verbose_name="Тариф"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    currency = models.CharField(max_length=3, default="RUB", verbose_name="Валюта")

    gateway = models.CharField(
        max_length=20,
        choices=Gateway.choices,
        default=Gateway.YOOKASSA,
        verbose_name="Шлюз",
    )
    external_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID платежа у провайдера",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    receipt_email = models.EmailField(verbose_name="Email чека", null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Доп. Metadata")
    provider_payload = models.JSONField(
        default=dict, blank=True, verbose_name="Ответ провайдера (Raw)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.gateway.upper()} {self.amount} {self.currency} ({self.status})"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

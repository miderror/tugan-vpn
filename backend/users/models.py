from django.db import models

from .validators import validate_utm_source


class User(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, primary_key=True, verbose_name="Телеграм ID"
    )
    username = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Юзернейм"
    )
    first_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Фамилия"
    )
    language_code = models.CharField(
        max_length=15, null=True, blank=True, verbose_name="Код языка"
    )

    utm_source = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="UTM-метка",
        validators=[validate_utm_source],
    )
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        verbose_name="Кто пригласил",
    )
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return f"id: {self.telegram_id}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

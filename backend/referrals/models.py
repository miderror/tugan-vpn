from django.db import models


class ReferralReward(models.Model):
    referrer = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="rewards_given",
        verbose_name="Кто получил бонус (пригласивший)",
    )
    referral = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="reward_triggered_by",
        verbose_name="Кто принес бонус (приглашенный)",
    )
    bonus_days_awarded = models.PositiveIntegerField(
        verbose_name="Начислено бонусных дней", default=7
    )
    awarded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата начисления")

    def __str__(self):
        return f"Бонус {self.bonus_days_awarded} дней для {self.referrer} за приглашение {self.referral}"

    class Meta:
        verbose_name = "Реферальное вознаграждение"
        verbose_name_plural = "Реферальные вознаграждения"
        ordering = ["-awarded_at"]

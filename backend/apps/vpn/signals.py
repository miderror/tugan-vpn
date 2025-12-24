import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Subscription
from .tasks import sync_subscription_task 

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subscription)
def on_subscription_save(sender, instance: Subscription, created: bool, **kwargs):
    update_fields = kwargs.get("update_fields")
    critical_fields = {"end_date", "is_vpn_client_active", "total_bytes_limit"}

    from pprint import pprint

    pprint(update_fields)

    if created or not update_fields or critical_fields.intersection(update_fields):
        logger.info(
            f"Подписка {instance.id} изменена. Запуск задачи синхронизации с 3x-ui."
        )
        sync_subscription_task.delay(instance.id)

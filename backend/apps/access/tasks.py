from typing import List, Optional

from asgiref.sync import async_to_sync
from celery import shared_task

from apps.access.services.subscription import SubscriptionService
from apps.access.services.sync import SyncService
from apps.access.services.traffic import TrafficService
from apps.notifications.tasks import send_mass_notification_task


@shared_task(queue="default", ignore_result=True)
def schedule_sync(user_ids: Optional[List[int]] = None):
    service = SyncService()
    async_to_sync(service.sync_all)(user_ids=user_ids)


@shared_task(queue="background", ignore_result=True)
def traffic_monitor_task():
    service = SyncService()
    usage_map = async_to_sync(service.collect_traffic)()
    disabled_ids = TrafficService.process_usage_report(usage_map)

    if disabled_ids:
        schedule_sync.delay(disabled_ids)


@shared_task(queue="background", ignore_result=True)
def monthly_reset_task():
    reset_ids = TrafficService.reset_monthly_limits()

    if reset_ids:
        schedule_sync.delay(reset_ids)


@shared_task(queue="background", ignore_result=True)
def process_manual_extension_task(
    mode: str,
    days: int,
    target_user_id: Optional[int],
    send_notification: bool,
    notification_text: str,
):
    user_ids = [target_user_id] if target_user_id else None
    affected_ids = SubscriptionService.extend_subscriptions(days, mode, user_ids)

    if affected_ids:
        schedule_sync.delay(affected_ids)

    if send_notification and notification_text and affected_ids:
        send_mass_notification_task.delay(affected_ids, notification_text)

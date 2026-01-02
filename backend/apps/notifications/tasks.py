from typing import List

from celery import shared_task

from apps.notifications.services.dispatcher import NotificationDispatcher


@shared_task(queue="default", ignore_result=True)
def send_individual_message_task(user_id: int, message: str):
    dispatcher = NotificationDispatcher()
    dispatcher.send_transactional(user_id, message)


@shared_task(queue="background", ignore_result=True)
def send_mass_notification_task(user_ids: List[int], message: str):
    dispatcher = NotificationDispatcher()
    dispatcher.send_broadcast(user_ids, message)


@shared_task(queue="background", ignore_result=True)
def check_expiry_notifications_task():
    dispatcher = NotificationDispatcher()
    dispatcher.process_expiry_rules()

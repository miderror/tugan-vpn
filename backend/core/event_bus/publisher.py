import logging

from celery import current_app
from django.db import transaction

from .base import IntegrationEvent
from .registry import get_subscribers

logger = logging.getLogger(__name__)


def publish(event: IntegrationEvent, use_transaction: bool = True):
    def _send():
        handlers = get_subscribers(event.event_name)
        if not handlers:
            return

        payload = event.model_dump()

        logger.info(
            f"EventBus: Publishing {event.event_name} to {len(handlers)} handlers."
        )
        for task_name in handlers:
            current_app.send_task(task_name, args=[payload])

    if use_transaction:
        transaction.on_commit(_send)
    else:
        _send()

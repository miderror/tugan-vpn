from functools import wraps
from typing import Type

from celery import shared_task

from .base import IntegrationEvent
from .registry import register_subscription


def subscribe(event_cls: Type[IntegrationEvent]):
    def decorator(func):
        task_name = f"{func.__module__}.{func.__name__}"

        register_subscription(event_cls, task_name)

        @shared_task(name=task_name, ignore_result=True)
        @wraps(func)
        def wrapper(event_payload: dict):
            event_obj = event_cls(**event_payload)
            return func(event_obj)

        return wrapper

    return decorator

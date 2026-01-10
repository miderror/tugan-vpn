from typing import Dict, List, Type

from .base import IntegrationEvent

_subscribers: Dict[str, List[str]] = {}


def register_subscription(event_cls: Type[IntegrationEvent], task_name: str):
    event_name = event_cls.event_name
    if event_name not in _subscribers:
        _subscribers[event_name] = []

    if task_name not in _subscribers[event_name]:
        _subscribers[event_name].append(task_name)


def get_subscribers(event_name: str) -> List[str]:
    return _subscribers.get(event_name, [])

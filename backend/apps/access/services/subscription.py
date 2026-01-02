import logging
from datetime import timedelta
from typing import List, Optional

from django.db import transaction
from django.db.models import Case, F, Q, Value, When
from django.utils import timezone

from apps.access.models import Subscription, SubscriptionMode

logger = logging.getLogger(__name__)


class SubscriptionService:
    @staticmethod
    def _build_filter(mode: str, user_ids: Optional[List[int]]) -> Q:
        now = timezone.now()
        if mode == SubscriptionMode.USER:
            return Q(user__telegram_id__in=user_ids) if user_ids else Q(pk__in=[])
        elif mode == SubscriptionMode.ACTIVE:
            return Q(end_date__gt=now)
        elif mode == SubscriptionMode.INACTIVE:
            return Q(end_date__lte=now)
        elif mode == SubscriptionMode.ALL:
            return Q()
        return Q(pk__in=[])

    @classmethod
    @transaction.atomic
    def extend_subscriptions(
        cls, days: int, mode: str, user_ids: Optional[List[int]] = None
    ) -> List[int]:
        now = timezone.now()
        delta = timedelta(days=days)
        filter_q = cls._build_filter(mode, user_ids)

        target_ids = list(
            Subscription.objects.filter(filter_q)
            .select_for_update()
            .values_list("user__telegram_id", flat=True)
        )

        if not target_ids:
            return []

        Subscription.objects.filter(user__telegram_id__in=target_ids).update(
            end_date=Case(
                When(end_date__gt=now, then=F("end_date") + delta),
                default=Value(now + delta),
            ),
            used_bytes=0,
            is_vpn_client_active=True,
            last_traffic_update=now,
        )

        logger.info(f"Extended subscriptions for {len(target_ids)} users. Mode: {mode}")
        return target_ids

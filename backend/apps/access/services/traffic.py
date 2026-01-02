import logging
from typing import Dict, List

from django.db import transaction
from django.utils import timezone

from apps.access.models import Subscription

logger = logging.getLogger(__name__)


class TrafficService:
    @staticmethod
    @transaction.atomic
    def process_usage_report(email_stats: Dict[str, int]) -> List[int]:
        if not email_stats:
            return []

        subs = (
            Subscription.objects.select_for_update()
            .filter(email__in=email_stats.keys())
            .only(
                "id",
                "email",
                "used_bytes",
                "total_bytes_limit",
                "is_vpn_client_active",
                "user_id",
            )
        )

        updates = []
        disabled_user_ids = []

        for sub in subs:
            usage = email_stats.get(sub.email, 0)
            if usage <= 0:
                continue

            sub.used_bytes += usage
            sub.last_traffic_update = timezone.now()

            if sub.is_vpn_client_active and sub.used_bytes >= sub.total_bytes_limit:
                sub.is_vpn_client_active = False
                disabled_user_ids.append(sub.user_id)

            updates.append(sub)

        if updates:
            Subscription.objects.bulk_update(
                updates,
                ["used_bytes", "last_traffic_update", "is_vpn_client_active"],
                batch_size=1000,
            )

        return disabled_user_ids

    @staticmethod
    def reset_monthly_limits() -> List[int]:
        threshold = timezone.now() - timezone.timedelta(days=30)

        qs = Subscription.objects.filter(
            end_date__gt=timezone.now(),
            used_bytes__gt=0,
            last_traffic_update__lt=threshold,
        )

        target_ids = list(qs.values_list("user__telegram_id", flat=True))

        if not target_ids:
            return []

        qs.update(
            used_bytes=0, last_traffic_update=timezone.now(), is_vpn_client_active=True
        )

        logger.info(f"Monthly reset applied to {len(target_ids)} users")
        return target_ids

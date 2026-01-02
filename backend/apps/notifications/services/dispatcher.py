import logging
from typing import List

from django.utils import timezone

from apps.notifications.models import NotificationRule, SentNotification
from apps.notifications.transports import TelegramTransport

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    def __init__(self):
        self.transport = TelegramTransport()

    def send_transactional(self, user_id: int, message: str) -> bool:
        return self.transport.send_single(user_id, message)

    def send_broadcast(self, user_ids: List[int], message: str) -> int:
        if not user_ids:
            return 0

        logger.info(f"Starting broadcast to {len(user_ids)} users.")
        count = self.transport.send_batch(user_ids, message)
        logger.info(f"Broadcast finished. Successfully sent: {count}/{len(user_ids)}")
        return count

    def process_expiry_rules(self):
        active_rules = NotificationRule.objects.filter(is_active=True)
        now = timezone.now()
        from apps.access.models import Subscription

        for rule in active_rules:
            hours = rule.trigger_hours_before_expiry

            target_time_start = now + timezone.timedelta(hours=hours)
            target_time_end = target_time_start + timezone.timedelta(
                minutes=59, seconds=59
            )

            expiring_subs = Subscription.objects.select_related("user").filter(
                end_date__gte=target_time_start,
                end_date__lte=target_time_end,
                is_vpn_client_active=True,
            )

            if not expiring_subs.exists():
                continue

            users_to_notify = []

            days_left = hours // 24
            hours_left = hours % 24

            formatted_text = rule.message_template.format(
                days=days_left, hours=hours_left
            )

            for sub in expiring_subs:
                already_sent = SentNotification.objects.filter(
                    user=sub.user,
                    rule=rule,
                    subscription_end_date_at_send_time=sub.end_date,
                ).exists()

                if not already_sent:
                    users_to_notify.append(sub.user)

                    SentNotification.objects.create(
                        user=sub.user,
                        rule=rule,
                        subscription_end_date_at_send_time=sub.end_date,
                    )

            if users_to_notify:
                ids = [u.telegram_id for u in users_to_notify]
                logger.info(f"Rule '{rule.name}': Notifying {len(ids)} users.")
                self.send_broadcast(ids, formatted_text)

from asgiref.sync import async_to_sync
from celery import shared_task

from .models import Subscription
from .services import VpnServerService


@shared_task(bind=True, max_retries=3)
def sync_subscription_task(self, subscription_id: int):
    try:
        sub = Subscription.objects.get(pk=subscription_id)
        service = VpnServerService()

        async_to_sync(service.sync_subscription)(sub)

        if not sub.is_vpn_client_active:
            sub.is_vpn_client_active = True
            sub.save(update_fields=["is_vpn_client_active"])

    except Subscription.DoesNotExist:
        pass
    except Exception as e:
        raise self.retry(exc=e)

import asyncio
import logging
from datetime import timedelta
from typing import List, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.utils import timezone

from apps.vpn.models import Subscription, SubscriptionMode

from .services import VpnServerService

logger = logging.getLogger(__name__)

LOCK_EXPIRE = 60 * 5
CHUNK_SIZE = 1000


@shared_task(bind=True, max_retries=0, ignore_result=True)
def process_subscription_management_task(
    self,
    action_id: str,
    mode: str,
    days: int,
    user_id: Optional[int] = None,
    send_notification: bool = False,
    notification_text: str = "",
):
    lock_key = f"vpn_mgmt_task_lock:{action_id}"

    with cache.lock(lock_key, timeout=LOCK_EXPIRE, blocking=False) as acquired:
        if not acquired:
            logger.warning(f"[Master] Duplicate task dropped. Action ID: {action_id}")
            return

        start_time = timezone.now()
        logger.info(f"[Master] Started. ID: {action_id}. Mode: {mode}")

        if mode == SubscriptionMode.USER and not user_id:
            logger.critical("[Master] Aborting: Mode is USER but user_id is missing!")
            return

        _perform_db_updates(mode, days, user_id)

        if send_notification:
            target_ids = _get_target_user_ids(mode, user_id)
            total_users = len(target_ids)

            if total_users > 0:
                logger.info(
                    f"[Master] Scheduling notifications for {total_users} users in chunks of {CHUNK_SIZE}"
                )

                for i in range(0, total_users, CHUNK_SIZE):
                    chunk_ids = target_ids[i : i + CHUNK_SIZE]

                    send_notification_chunk_task.delay(
                        chunk_ids=chunk_ids,
                        text=notification_text,
                        meta_info=f"{action_id}_chunk_{i}",
                    )
            else:
                logger.info("[Master] No users to notify.")

        duration = timezone.now() - start_time
        logger.info(
            f"[Master] DB updated & tasks scheduled. Took: {duration.total_seconds()}s"
        )


@shared_task(bind=True, max_retries=3, ignore_result=True)
def send_notification_chunk_task(self, chunk_ids: List[int], text: str, meta_info: str):
    logger.info(f"[ChunkWorker] Starting chunk {meta_info} for {len(chunk_ids)} users.")
    async_to_sync(_send_async_chunk)(chunk_ids, text)
    logger.info(f"[ChunkWorker] Finished chunk {meta_info}")


def _get_target_user_ids(mode: str, user_id: Optional[int]) -> List[int]:
    now = timezone.now()
    qs = Subscription.objects.all()

    if mode == SubscriptionMode.USER:
        qs = qs.filter(user__telegram_id=user_id)
    elif mode == SubscriptionMode.ACTIVE:
        qs = qs.filter(end_date__gt=now)
    elif mode == SubscriptionMode.INACTIVE:
        qs = qs.filter(end_date__lte=now)

    return list(qs.values_list("user__telegram_id", flat=True))


def _perform_db_updates(mode: str, days: int, user_id: Optional[int]):
    now = timezone.now()
    delta = timedelta(days=days)
    qs = Subscription.objects.all()

    if mode == SubscriptionMode.USER:
        qs = qs.filter(user__telegram_id=user_id)

    if mode != SubscriptionMode.INACTIVE:
        count = qs.filter(end_date__gt=now).update(end_date=F("end_date") + delta)
        logger.info(f"DB: Extended {count} active subs.")

    if mode != SubscriptionMode.ACTIVE:
        count = qs.filter(end_date__lte=now).update(end_date=now + delta)
        logger.info(f"DB: Revived {count} inactive subs.")


async def _send_async_chunk(user_ids: List[int], text: str):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    sem = asyncio.Semaphore(20)

    async def send_one(chat_id):
        async with sem:
            try:
                await bot.send_message(chat_id=chat_id, text=text)
            except TelegramRetryAfter as e:
                logger.info(f"Rate limit hit. Sleeping {e.retry_after}s.")
                await asyncio.sleep(e.retry_after)
                try:
                    await bot.send_message(chat_id=chat_id, text=text)
                except Exception:
                    pass
            except TelegramForbiddenError:
                pass
            except Exception as e:
                logger.error(f"Send failed {chat_id}: {e}")

            await asyncio.sleep(0.04)

    await asyncio.gather(*(send_one(uid) for uid in user_ids))

    await bot.session.close()


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

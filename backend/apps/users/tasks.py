import logging
from datetime import timedelta

import requests
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import User

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, rate_limit="2/s", ignore_result=True)
def update_user_avatar_task(self, user_id: int) -> None:
    try:
        user = User.objects.get(telegram_id=user_id)
        bot_token = settings.TELEGRAM_BOT_TOKEN
        base_url = f"https://api.telegram.org/bot{bot_token}"

        resp = requests.get(
            f"{base_url}/getUserProfilePhotos",
            params={"user_id": user_id, "limit": 1},
            timeout=10,
        )

        if resp.status_code != 200:
            logger.warning(f"Telegram API Error {resp.status_code} for user {user_id}")
            return

        data = resp.json()
        photos = data.get("result", {}).get("photos", [])

        if not photos:
            logger.info(f"User {user_id} has no profile photos.")
            return

        file_id = photos[0][0]["file_id"]

        file_resp = requests.get(
            f"{base_url}/getFile", params={"file_id": file_id}, timeout=10
        )

        if file_resp.status_code != 200:
            logger.warning(f"Failed to get file path for user {user_id}")
            return

        file_path = file_resp.json()["result"]["file_path"]

        dl_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        image_content = requests.get(dl_url, timeout=20).content

        filename = f"{user_id}.jpg"

        if user.avatar:
            user.avatar.delete(save=False)

        user.avatar.save(filename, ContentFile(image_content), save=False)
        user.avatar_updated_at = timezone.now()
        user.save(update_fields=["avatar", "avatar_updated_at"])

        logger.info(f"Successfully updated avatar for user {user_id}")

    except Exception as e:
        logger.error(f"Avatar update exception for {user_id}: {e}")
        raise self.retry(exc=e, countdown=300)


@shared_task(ignore_result=True)
def schedule_daily_avatar_updates() -> None:
    threshold = timezone.now() - timedelta(days=3)
    users_ids = User.objects.filter(avatar_updated_at__lt=threshold).values_list(
        "telegram_id", flat=True
    )[:1000]

    for uid in users_ids:
        update_user_avatar_task.delay(uid)

    logger.info(f"Scheduled avatar updates for {len(users_ids)} users.")

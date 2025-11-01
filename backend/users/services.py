import logging
from typing import Optional

from django.core.exceptions import ValidationError

from .models import User
from .validators import validate_utm_source

logger = logging.getLogger(__name__)


def is_valid_utm_source(value: str) -> bool:
    try:
        validate_utm_source(value)
        return True
    except ValidationError:
        return False


def process_start_param(new_user: User, start_param: Optional[str]) -> None:
    if not start_param:
        return

    if start_param.isdigit():
        _handle_referral(new_user, int(start_param))
    elif is_valid_utm_source(start_param):
        _handle_utm_source(new_user, start_param)
    else:
        logger.warning(
            f"Invalid start_param for user {new_user.telegram_id}: '{start_param}'"
        )


def _handle_referral(new_user: User, referrer_id: int) -> None:
    if new_user.telegram_id == referrer_id:
        logger.warning(f"User {new_user.telegram_id} tried to refer themselves.")
        return

    try:
        referrer = User.objects.get(telegram_id=referrer_id)
        new_user.referred_by = referrer
        new_user.save(update_fields=["referred_by"])
        logger.info(f"User {new_user} was referred by {referrer}")
    except User.DoesNotExist:
        logger.warning(
            f"Referrer with id {referrer_id} not found for user {new_user.telegram_id}"
        )


def _handle_utm_source(new_user: User, utm_source: str) -> None:
    new_user.utm_source = utm_source
    new_user.save(update_fields=["utm_source"])
    logger.info(f"User {new_user} registered with UTM source: {utm_source}")

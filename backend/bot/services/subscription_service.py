from asgiref.sync import sync_to_async
from api.models import Key, Notification, Payment
from services.notification_service import (
    send_subscription_expiry_notification, send_trial_period_end_notification,
    send_trial_activation_notification
)
from datetime import datetime, timedelta, timezone


async def check_subscriptions():
    now = datetime.now(timezone.utc)
    
    expired_keys = await sync_to_async(
        lambda: list(Key.objects.filter(
            can_claim_gift=False,
            expiry_time__lte=int(now.timestamp() * 1000),
        ).select_related('user'))
    )()
    
    print(f"Найдено ключей с истекшей подпиской: {len(expired_keys)}")
    
    for key in expired_keys:
        has_payments = await sync_to_async(
            Payment.objects.filter(user__tg_id=key.user.tg_id).exists
        )()

        notification_exists = await sync_to_async(
            Notification.objects.filter(
                tg_id=key.user.tg_id,
                notification_type="trial_period_end"
            ).exists
        )()

        if not has_payments and not notification_exists:
            await send_trial_period_end_notification(key.user.tg_id)

            await Notification.objects.acreate(
                tg_id=key.user.tg_id,
                notification_type="trial_period_end"
            )
            print(f"Уведомление о завершении пробного периода отправлено пользователю {key.user.tg_id}.")


    keys_to_notify = await sync_to_async(
        lambda: list(Key.objects.filter(
            is_active=True,
            expiry_time__lte=int((now + timedelta(hours=24)).timestamp() * 1000),
            expiry_time__gt=int(now.timestamp() * 1000),
        ).select_related('user'))
    )()

    print(f"Найдено ключей для уведомления: {len(keys_to_notify)}")
    
    for key in keys_to_notify:
        notification_exists = await sync_to_async(
            Notification.objects.filter(
                tg_id=key.user.tg_id,
                notification_type="subscription_expiry"
            ).exists
        )()

        if not notification_exists:
            await send_subscription_expiry_notification(key.user.tg_id, key.expiry_time)
            
            await Notification.objects.acreate(
                tg_id=key.user.tg_id,
                notification_type="subscription_expiry"
            )
            print(f"Уведомление отправлено пользователю {key.user.tg_id}.")

async def check_inactive_users_and_notify():
    try:
        now = datetime.now(timezone.utc)
        time_threshold = now - timedelta(hours=5)

        inactive_keys = await sync_to_async(list)(
            Key.objects.filter(
                tried_to_connect=False,
                created_at__lte=time_threshold,
            ).select_related('user')
        )

        print(f"Найдено ключей для уведомления: {len(inactive_keys)}")

        for key in inactive_keys:
            notification_exists = await sync_to_async(
                Notification.objects.filter(
                    tg_id=key.user.tg_id,
                    notification_type="trial_activation_reminder"
                ).exists
            )()

            if not notification_exists:
                await send_trial_activation_notification(key.user.tg_id)

                await Notification.objects.acreate(
                    tg_id=key.user.tg_id,
                    notification_type="trial_activation_reminder"
                )
                print(f"Уведомление отправлено пользователю {key.user.tg_id}.")
    except Exception as e:
        print(f"Ошибка при проверке неактивных пользователей: {e}")

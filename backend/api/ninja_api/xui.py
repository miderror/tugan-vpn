from ..services import xui
from ninja import Router
from django.conf import settings
from ..models import Key
from datetime import datetime, timedelta, timezone

router = Router()

@router.get("/vpn_config/")
async def get_vpn_config(request):
    try:
        current_user = request.tg_user
        key = await Key.objects.aget(user=current_user)
        if not key.tried_to_connect:
            key.tried_to_connect = True
            await key.asave()
        vpn_url = f"{settings.SUB_PATH}{key.access_token}"
        print('Отдаю часть url:', vpn_url)
        return {
            "vpn_url": vpn_url
        }
    except Exception as e:
        print("Ошибка при получении конфига:", e)
        return {"error": "error"}

@router.get("/current_user/")
async def current_user(request):
    try:
        current_user = request.tg_user
        key = await Key.objects.aget(user=current_user)
        print('ninja django:', current_user)
        now_time = int(datetime.now(timezone.utc).timestamp() * 1000)
        active_user = key.expiry_time > now_time and key.is_active
        return {
            "usage": f"{key.used_gb}/{key.total_gb} GB",
            "subscriptionDate": key.expiry_date if active_user else "неактивна",
            "can_claim_gift": key.can_claim_gift
        }
    except Exception as e:
        return {}

@router.post("/claim_gift/")
async def claim_gift(request):
    try:
        current_user = request.tg_user
        key = await Key.objects.filter(user=current_user).afirst()
        if not key or not key.can_claim_gift:
            return {"error": "error"}
        key.can_claim_gift = False
        await key.asave()

        return {"status": "success"}
    except Exception as e:
        print(f"Ошибка при получении подарка: {e}")
        return {"error": "error"}

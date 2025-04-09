import base64
import json
from ninja import Router
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.conf import settings
from ..services.xui import get_combined_subscriptions
from ..models import Key

router = Router()


@router.get("/get_user_ip/")
def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return JsonResponse({"ip": ip})

@router.get("/ruleset/")
async def get_ruleset(request):
    try:
        ruleset = [
            {
                "enabled": True,
                "remarks": "Трафик на российские IP-адреса напрямую",
                "domainMatcher": "linear",
                "domain": [],
                "ip": ["geoip:ru"],
                "outboundTag": "direct"
            },
            {
                "enabled": True,
                "remarks": "Трафик на домены .ru напрямую",
                "outboundTag": "direct",
                "domain": ["regexp:.*\\.ru$"]
            },
            {
                "enabled": True,
                "remarks": "Трафик на популярные сервисы напрямую",
                "outboundTag": "direct",
                "domainMatcher": "hybrid",
                "domain": [
                    "geosite:telegram",
                    "geosite:whatsapp",
                    "geosite:apple",
                    "geosite:google",
                    "geosite:itunes"
                ]
            }
        ]

        response = HttpResponse(json.dumps(ruleset), content_type="application/json")
        response["Content-Disposition"] = "inline"
        return response
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return HttpResponseBadRequest("Ошибка сервера")

@router.get(settings.SUB_PATH + "/{access_token}")
async def get_subscription(request, access_token: str):
    try:
        key = await Key.objects.aget(access_token=access_token)

        combined_subscriptions = await get_combined_subscriptions(key.sub_id)

        base64_encoded = base64.b64encode("\n".join(combined_subscriptions).encode("utf-8")).decode("utf-8")

        expiry_time_seconds = key.expiry_time // 1000
        response = HttpResponse(base64_encoded, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = "inline"
        response["profile-update-interval"] = "2"
        response["profile-title"] = "base64:VFVHQU4gVlBOIPCfjI8="
        response["subscription-userinfo"] = f"upload=0; download={key.used_bytes}; total={key.total_bytes}; expire={expiry_time_seconds}"

        return response
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return HttpResponseBadRequest("Ошибка сервера")

@router.get("/")
async def handle_root(request, url: str = None):
    if url and url.startswith("v2raytun://import-sub?url="):
        subscription_url = url.split("url=")[1]
        return redirect(subscription_url)
    
    return HttpResponseBadRequest("Invalid URL format")
import json
import re
import uuid
from django.http import JsonResponse
from ninja import Router
from yookassa import Payment as YookassaPayment, Configuration
from yookassa.domain.notification import WebhookNotificationFactory
from ..services import xui
from django.conf import settings
from ..models import Tariff, Payment, User
from asgiref.sync import sync_to_async
from ninja import Schema
from bot.services.notification_service import send_payment_success_notification, send_admin_payment_notification

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

class CreatePaymentSchema(Schema):
    tariff_id: int
    email: str
    
    def validate(self):
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', self.email):
            raise ValueError('Некорректный email')
        
        if len(self.email) > 254:
            raise ValueError('Email слишком длинный (максимум 254 символа)')

router = Router()

@router.post("/webhook/")
async def yookassa_webhook(request):
    try:
        event_json = request.body.decode('utf-8')
        event_dict = json.loads(event_json)

        notification = WebhookNotificationFactory().create(event_dict)

        if notification.object.status == "succeeded":
            payment_id = notification.object.id
            user_id = notification.object.metadata.get('user_id')
            tariff_id = notification.object.metadata.get('tariff_id')

            print(f"Payment ID: {payment_id}")
            print(f"User ID: {user_id}")
            print(f"Tariff ID: {tariff_id}")

            payment_exists = await sync_to_async(Payment.objects.filter(payment_id=payment_id).exists)()
            if payment_exists:
                print(f"Payment {payment_id} already processed.")
                return JsonResponse({'status': 'success'})
            
            tariff = await Tariff.objects.aget(id=tariff_id)
            print(f"Tarriff period days: {tariff.period_days}")
            await xui.extend_access(
                user_id,
                days=tariff.period_days,
                total_bytes=int(settings.TOTAL_GB * 1024 * 1024 * 1024)
            )

            user = await sync_to_async(User.objects.get)(tg_id=user_id)
            await sync_to_async(Payment.objects.create)(
                user=user,
                amount=tariff.total,
                payment_system="yookassa",
                status="success",
                payment_id=payment_id,
            )
            
            await send_payment_success_notification(user_id, tariff.total, tariff.duration)

            await send_admin_payment_notification(
                user_id=user_id,
                username=user.username,
                payment_id=payment_id,
                amount=tariff.total,
                duration=tariff.duration,
                payment_system="yookassa"
            )
            print(f"Payment ID: {payment_id} processed successfully.")

        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': 'error check webhook'}, status=500)


@router.post("/create_payment/")
async def yookassa_create_payment(request, payload: CreatePaymentSchema):
    try:
        payload.validate()
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    if not payload.tariff_id or not payload.email:
        return JsonResponse({"error": "tariff_id and email is required"}, status=400)

    tariff = await sync_to_async(Tariff.objects.filter(id=payload.tariff_id).first)()
    if not tariff:
        return JsonResponse({"error": "Tariff not found"}, status=404)
    
    user_id = request.tg_user.tg_id
    customer_name = f'{request.tg_user.first_name} {request.tg_user.last_name}'
    return_url = settings.WEBAPP_URL
    print("Find email in create payment:", payload.email)

    try:
        yookassa_payment = YookassaPayment.create({
            "amount": {
                "value": str(tariff.total),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect", 
                "return_url": return_url
            },
            "capture": True,
            "description": f"Оплата подписки на {tariff.duration}",
            "metadata": {
                "user_id": user_id,
                "tariff_id": payload.tariff_id
            },
            "receipt": {
                "customer": {
                    "full_name": customer_name,
                    "email": payload.email,
                    "phone": "+79000000000"
                },
                "tax_system_code": 1,
                "items": [
                    {
                        "description": "Пополнение баланса",
                        "quantity": "1.00",
                        "amount": {"value": str(tariff.total), "currency": "RUB"},
                        "vat_code": 6,
                        "payment_subject": "service",
                        "payment_mode": "full_prepayment"
                    }
                ],
            },
        }, idempotency_key=str(uuid.uuid4()))

        print(yookassa_payment.confirmation.confirmation_url)
        return {
            'payment_url': yookassa_payment.confirmation.confirmation_url,
        }

    except Exception as e:
        return JsonResponse({"error": "error creating payment"}, status=500)

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from django.conf import settings
from bot import bot, dp
from api.services.xui import check_traffic_and_disable_users, periodic_traffic_reset
from services.subscription_service import check_subscriptions, check_inactive_users_and_notify

async def periodic_traffic_check(interval: int = 900):
    while True:
        print("Запуск проверки отключения юзеров из-за трафика...")
        await check_traffic_and_disable_users()
        await asyncio.sleep(interval)

async def check_subscriptions_task(interval: int = 3600):
    while True:
        print("Запуск проверки подписок...")
        await check_subscriptions()
        await asyncio.sleep(interval)

async def periodic_traffic_reset_task(interval: int = 86400):
    while True:
        print("Запуск проверки необходимости сброса трафика...")
        await periodic_traffic_reset()
        await asyncio.sleep(interval)

async def check_inactive_users_and_notify_task(interval: int = 3600):
    while True:
        print("Запуск напоминания о пробном периоде...")
        await check_inactive_users_and_notify()
        await asyncio.sleep(interval)


async def on_startup(app):
    await bot.set_webhook(settings.WEBHOOK_URL)
    print(f"Вебхук установлен: {settings.WEBHOOK_URL}")
    app["tasks"] = [
        asyncio.create_task(periodic_traffic_check()),
        asyncio.create_task(periodic_traffic_reset_task()),
        asyncio.create_task(check_subscriptions_task()),
        asyncio.create_task(check_inactive_users_and_notify_task()),
    ]

async def on_shutdown(app):
    await bot.delete_webhook()
    print("Вебхук удален.")

async def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.WEBHOOK_HOST, port=settings.WEBHOOK_PORT)
    await site.start()

    print(f"Сервер запущен на {settings.WEBHOOK_HOST}:{settings.WEBHOOK_PORT}")
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        print("Получен сигнал SIGINT (Ctrl+C). Остановка сервера...")
    finally:
        await site.stop()
        await runner.cleanup()
        if "tasks" in app:
            for task in app["tasks"]:
                task.cancel()
            await asyncio.wait(app["tasks"])
        print("Сервер остановлен.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Сервер остановлен.")
import argparse
import sys

import httpx

from app.config.settings import settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Telegram Bot Webhook")
    parser.add_argument(
        "action", choices=["set", "delete"], help="Action to perform: set or delete"
    )
    args = parser.parse_args()

    bot_token = settings.telegram_bot_token
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN is not set in environment.")
        sys.exit(1)

    base_url = f"https://api.telegram.org/bot{bot_token}"

    if args.action == "set":
        webhook_url = settings.telegram_webhook_url
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message"],
            "drop_pending_updates": False,
        }

        if settings.telegram_webhook_secret:
            payload["secret_token"] = settings.telegram_webhook_secret

        print(f"🔄 Установка вебхука на адрес: {webhook_url}...")
        try:
            resp = httpx.post(f"{base_url}/setWebhook", json=payload, timeout=10.0)
            res = resp.json()
            if res.get("ok"):
                print("✅ Вебхук успешно установлен!")
            else:
                print(f"❌ Ошибка установки вебхука: {res.get('description')}")
        except Exception as e:
            print(f"❌ Сетевая ошибка при установке вебхука: {e}")

    elif args.action == "delete":
        print("🔄 Удаление вебхука...")
        try:
            resp = httpx.post(f"{base_url}/deleteWebhook", timeout=10.0)
            res = resp.json()
            if res.get("ok"):
                print("✅ Вебхук успешно удален!")
            else:
                print(f"❌ Ошибка при удалении вебхука: {res.get('description')}")
        except Exception as e:
            print(f"❌ Сетевая ошибка при удалении вебхука: {e}")


if __name__ == "__main__":
    main()

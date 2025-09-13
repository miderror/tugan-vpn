from datetime import datetime, timedelta, timezone
import hashlib
import uuid
import secrets
import aiohttp
import base64
from py3xui import AsyncApi, Client
from ..models import Key, User, Notification
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async

def generate_secure_sub_id(tg_id):
    random_part = secrets.token_urlsafe(16)
    random_part = random_part.replace("_", "-")
    return f"{tg_id}{random_part}"

def generate_unique_email(tg_id):
    unique_id = uuid.uuid4().hex
    return f"{unique_id}{tg_id}"

def generate_access_token(tg_id):
    unique_part = str(uuid.uuid4())
    token = hashlib.sha256(f"{tg_id}{unique_part}".encode()).hexdigest()
    return token

async def fetch_url_content(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                if response.status == 200:
                    content = await response.text()
                    return base64.b64decode(content).decode("utf-8").split("\n")
                else:
                    print(f"Не удалось получить {url}, статус: {response.status}")
                    return []
    except Exception as e:
        print(f"Ошибка при получении {url}: {e}")
        return []

async def get_least_loaded_server(cluster):
    least_loaded_server = None
    min_online_users = float('inf')

    for server_name, server_config in cluster.items():
        try:
            xui = AsyncApi(
                server_config['API_URL'],
                username=settings.XUI_ADMIN_USERNAME,
                password=settings.XUI_ADMIN_PASSWORD,
            )
            await xui.login()

            online_users = await xui.client.online()
            online_users_count = len(online_users)

            if online_users_count < min_online_users:
                min_online_users = online_users_count
                least_loaded_server = server_config
        except Exception as e:
            print(f"Ошибка при получении данных с сервера {server_name}: {e}")

    return least_loaded_server

async def get_combined_subscriptions(sub_id):
    urls = []

    for cluster_name, cluster in settings.XUI_CLUSTERS.items():
        least_loaded_server = await get_least_loaded_server(cluster)
        if least_loaded_server:
            server_subscription_url = f"{least_loaded_server['SUBSCRIPTION']}/{sub_id}"
            urls.append((server_subscription_url, least_loaded_server['NAME']))

    combined_subscriptions = []
    for url, server_name in urls:
        lines = await fetch_url_content(url)
        print('lines', lines)
        for line in lines:
            print('line:', line)
            if "#" in line:
                print(type (line))
                base_url, _ = line.split("#", 1)
                subscription = f"{base_url}#{server_name}"
                combined_subscriptions.append(subscription)

    combined_subscriptions = list(set(filter(None, combined_subscriptions)))
    return combined_subscriptions

async def reset_traffic(key):
    key.is_active = True
    key.used_bytes = 0
    key.next_reset_date = datetime.now(timezone.utc) + timedelta(days=30)
    await sync_to_async(key.save)()

    for cluster_name, cluster in settings.XUI_CLUSTERS.items():
        for server_name, server_config in cluster.items():
            try:
                xui = AsyncApi(
                    server_config['API_URL'],
                    username=settings.XUI_ADMIN_USERNAME,
                    password=settings.XUI_ADMIN_PASSWORD,
                )
                await xui.login()

                
                await xui.client.reset_stats(
                    inbound_id=server_config['INBOUND_ID'],
                    email=key.email
                )

                client = await xui.client.get_by_email(key.email)
                client.id = key.client_id
                client.expiry_time = key.expiry_time
                client.flow = "xtls-rprx-vision"
                client.total_gb = key.total_bytes
                client.sub_id = key.sub_id
                client.limit_ip = 1
                client.enable = key.is_active
                await xui.client.update(key.client_id, client)
                print("Обновлен")
                print(f"Сброс на сервере {server_name} для {key.sub_id}")
            except Exception as e:
                print(f"Ошибка при сбросе трафика на сервере {server_name} (кластер {cluster_name}): {e}")

async def create_client(tg_id, days, total_bytes, is_active):
    try:
        user = await User.objects.aget(tg_id=tg_id)
    except ObjectDoesNotExist:
        print(f"Пользователь с tg_id={tg_id} не найден.")
        return

    now_time = datetime.now(timezone.utc)
    expiry_time = int((now_time + timedelta(days=days)).timestamp() * 1000)
    client_id = str(uuid.uuid4())
    sub_id = generate_secure_sub_id(tg_id)
    email = generate_unique_email(tg_id)
    access_token = str(generate_access_token(tg_id))
    next_reset_date = now_time + timedelta(days=30)
    
    key = await Key.objects.acreate(
        user=user,
        client_id=client_id,
        email=email,
        expiry_time=expiry_time,
        sub_id=sub_id,
        total_bytes=total_bytes,
        used_bytes=0,
        is_active=is_active,
        access_token=access_token,
        next_reset_date=next_reset_date,
    )
    
    try:
        for cluster_name, cluster in settings.XUI_CLUSTERS.items():
            for server_name, server_config in cluster.items():
                xui = AsyncApi(
                    server_config['API_URL'],
                    username=settings.XUI_ADMIN_USERNAME,
                    password=settings.XUI_ADMIN_PASSWORD,
                )
                await xui.login()

                client = Client(
                    id=client_id,
                    email=email.lower(),
                    limit_ip=1,
                    total_gb=total_bytes,
                    expiry_time=expiry_time,
                    enable=is_active,
                    tg_id=tg_id,
                    sub_id=sub_id,
                    flow="xtls-rprx-vision",
                )

                await xui.client.add(server_config['INBOUND_ID'], [client])
    except Exception as e:
        print(f"Ошибка при создании клиента на серверах: {e}")
        raise e

async def extend_access(tg_id, days, total_bytes):
    try:
        user = await User.objects.aget(tg_id=tg_id)
    except ObjectDoesNotExist:
        print(f"Пользователь с tg_id={tg_id} не найден.")
        return

    key = await sync_to_async(Key.objects.filter(user=user).first)()
    if not key:
        print(f"Ключ для юзера {user.tg_id} не найден")
        return

    now = int(datetime.now(timezone.utc).timestamp() * 1000)

    new_expiry_time = (days * 24 * 60 * 60 * 1000) + max(key.expiry_time, now)

    for cluster_name, cluster in settings.XUI_CLUSTERS.items():
        for server_name, server_config in cluster.items():
            try:
                xui = AsyncApi(
                    server_config['API_URL'],
                    username=settings.XUI_ADMIN_USERNAME,
                    password=settings.XUI_ADMIN_PASSWORD,
                )
                await xui.login()

                client = await xui.client.get_by_email(key.email)
                if not client:
                    print(f"Клиент с email {key.email} не найден на сервере {server_name}.")
                    continue

                client.id = key.client_id
                client.expiry_time = new_expiry_time
                client.flow = "xtls-rprx-vision"
                client.total_gb = total_bytes
                client.sub_id = key.sub_id
                client.limit_ip = 1
                client.enable = key.is_active

                await xui.client.update(key.client_id, client)
            except Exception as e:
                print(f"Ошибка при обновлении клиента на сервере {server_name} (кластер {cluster_name}): {e}")

    key.expiry_time = new_expiry_time
    key.total_bytes = total_bytes
    key.is_active = True
    await key.asave()

    await reset_traffic(key)

    await sync_to_async(Notification.objects.filter(
        tg_id=user.tg_id,
        notification_type="subscription_expiry"
    ).delete)()

async def disable_user_on_all_servers(key):
    for cluster_name, cluster in settings.XUI_CLUSTERS.items():
        for server_name, server_config in cluster.items():
            try:
                xui = AsyncApi(
                    server_config['API_URL'],
                    username=settings.XUI_ADMIN_USERNAME,
                    password=settings.XUI_ADMIN_PASSWORD,
                )
                await xui.login()

                client = await xui.client.get_by_email(key.email)
                if not client:
                    print(f"Клиент с email {key.email} не найден на сервере {server_name}.")
                    continue

                client.id = key.client_id
                client.expiry_time = key.expiry_time
                client.flow = "xtls-rprx-vision"
                client.total_gb = key.total_bytes
                client.enable = False
                client.sub_id = key.sub_id
                client.limit_ip = 1

                await xui.client.update(key.client_id, client)
                user = await sync_to_async(lambda: key.user)()
                print(f"Пользователь {user.tg_id} отключен на сервере {server_name}.")

            except Exception as e:
                print(f"Ошибка при отключении клиента на сервере {server_name} (кластер {cluster_name}): {e}")

async def check_traffic_and_disable_users():
    active_keys = await sync_to_async(Key.objects.filter)(is_active=True)
    active_keys = await sync_to_async(list)(active_keys)

    print("Начало проверки")
    for key in active_keys:
        total_used_bytes = 0

        for cluster_name, cluster in settings.XUI_CLUSTERS.items():
            for server_name, server_config in cluster.items():
                try:
                    xui = AsyncApi(
                        server_config['API_URL'],
                        username=settings.XUI_ADMIN_USERNAME,
                        password=settings.XUI_ADMIN_PASSWORD,
                    )
                    await xui.login()

                    client = await xui.client.get_by_email(key.email)
                    print(client)
                    print(*client)
                    if client:
                        total_used_bytes += client.up + client.down
                        print(total_used_bytes)

                except Exception as e:
                    print(f"Ошибка при получении статистики с сервера {server_name} (кластер {cluster_name}): {e}")

        key.used_bytes = max(total_used_bytes, key.used_bytes)
        await sync_to_async(key.save)()
        print("off user?:", total_used_bytes >= key.total_bytes)
        print(key.total_bytes)
        if total_used_bytes >= key.total_bytes:
            key.is_active = False
            await sync_to_async(key.save)()
            user = await sync_to_async(lambda: key.user)()
            print(f"Пользователь {user.tg_id} отключен за превышение лимита трафика.")
            await disable_user_on_all_servers(key)
    print("Конец проверки")

async def periodic_traffic_reset():
    now = datetime.now(timezone.utc)
    keys_to_reset = await sync_to_async(Key.objects.filter)(
        next_reset_date__lte=now,
        expiry_time__gt=int(now.timestamp() * 1000)
    )
    keys_to_reset = await sync_to_async(list)(keys_to_reset)

    for key in keys_to_reset:
        await reset_traffic(key)
        print(f"Трафик для пользователя {key.sub_id} сброшен.")

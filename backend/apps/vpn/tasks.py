from asgiref.sync import async_to_sync
from celery import shared_task

from apps.vpn.services.sync import VpnSyncService


@shared_task(queue="default", ignore_result=True)
def sync_user_everywhere_task(sub_id: int):
    svc = VpnSyncService()
    async_to_sync(svc.sync_user_everywhere)(sub_id)


@shared_task(queue="default", ignore_result=True)
def sync_user_to_server_task(sub_id: int, server_id: int):
    svc = VpnSyncService()
    async_to_sync(svc.sync_user_to_server)(sub_id, server_id)


@shared_task(queue="background", ignore_result=True)
def sync_server_full_task(server_id: int):
    svc = VpnSyncService()
    async_to_sync(svc.sync_server_full)(server_id)


@shared_task(queue="background", ignore_result=True)
def sync_all_servers_full_task():
    svc = VpnSyncService()
    async_to_sync(svc.sync_all_servers_full)()

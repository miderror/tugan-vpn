from typing import List

from apps.vpn.models import Subscription, VpnServer

from .dtos import ServerConnDTO, UserSyncDTO


class VpnSelector:
    @staticmethod
    def _map_user(data: dict) -> UserSyncDTO:
        return UserSyncDTO(
            telegram_id=data["user__telegram_id"],
            vless_uuid=data["vless_uuid"],
            email=data["email"],
            is_enable=data["is_vpn_client_active"],
            total_gb=data["total_bytes_limit"],
            expiry_time_ms=int(data["end_date"].timestamp() * 1000),
            sub_id=data["sub_id"],
        )

    @staticmethod
    def _map_server(data: dict) -> ServerConnDTO:
        return ServerConnDTO(
            id=data["id"],
            api_url=data["credentials"]["api_url"],
            username=data["credentials"]["username"],
            password=data["credentials"]["password"],
            inbound_id=data["inbound_id"],
        )

    @classmethod
    def get_user(cls, sub_id: int) -> UserSyncDTO:
        data = (
            Subscription.objects.filter(pk=sub_id)
            .values(
                "user__telegram_id",
                "vless_uuid",
                "email",
                "is_vpn_client_active",
                "total_bytes_limit",
                "end_date",
                "sub_id",
            )
            .first()
        )
        if not data:
            raise ValueError(f"Subscription {sub_id} not found")
        return cls._map_user(data)

    @classmethod
    def get_server(cls, server_id: int) -> ServerConnDTO:
        data = (
            VpnServer.objects.filter(pk=server_id)
            .values("id", "credentials", "inbound_id")
            .first()
        )
        if not data:
            raise ValueError(f"Server {server_id} not found")
        return cls._map_server(data)

    @classmethod
    def get_all_active_servers(cls) -> List[ServerConnDTO]:
        data = VpnServer.objects.filter(is_active=True).values(
            "id", "credentials", "inbound_id"
        )
        return [cls._map_server(s) for s in data]

    @classmethod
    def get_all_users(cls) -> List[UserSyncDTO]:
        data = Subscription.objects.all().values(
            "user__telegram_id",
            "vless_uuid",
            "email",
            "is_vpn_client_active",
            "total_bytes_limit",
            "end_date",
            "sub_id",
        )
        return [cls._map_user(u) for u in data]

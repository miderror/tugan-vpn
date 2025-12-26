from rest_framework import serializers

from apps.users.models import User


class ReferralUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="telegram_id")

    class Meta:
        model = User
        fields = ("id", "username")

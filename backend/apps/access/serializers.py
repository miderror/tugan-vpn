from rest_framework import serializers

from .models import Tariff


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = (
            "id",
            "display_name",
            "duration_days",
            "price",
            "is_bestseller",
            "original_price",
        )

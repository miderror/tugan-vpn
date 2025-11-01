from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Tariff
from .serializers import TariffSerializer


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tariff.objects.filter(is_active=True)
    serializer_class = TariffSerializer
    permission_classes = [IsAuthenticated]

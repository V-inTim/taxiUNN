from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    TaxiFareSerializer,
    TaxiFareCreateSerializer,
)
from .models import TaxiFare


class TaxiFareCreateView(CreateAPIView):
    """View for create taxi fare."""

    queryset = TaxiFare.objects.all()
    serializer_class = TaxiFareCreateSerializer
    permission_classes = [IsAuthenticated]


class TaxiFareView(RetrieveUpdateDestroyAPIView):
    """View for retrieve, update and remove taxi fare."""

    queryset = TaxiFare.objects.all()
    serializer_class = TaxiFareSerializer
    permission_classes = [IsAuthenticated]

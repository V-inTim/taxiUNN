from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    ListAPIView,
)

from .serializers import (
    TaxiFareSerializer,
    TaxiFareCreateSerializer,
)
from .models import TaxiFare
from admin_auth.authentication import (
    IsAuthenticatedAdmin,
    AdminJWTAuthentication,
)


class TaxiFareCreateView(CreateAPIView):
    """View for create taxi fare."""

    queryset = TaxiFare.objects.all()
    serializer_class = TaxiFareCreateSerializer
    permission_classes = [IsAuthenticatedAdmin]
    authentication_classes = [AdminJWTAuthentication]


class TaxiFareView(RetrieveUpdateDestroyAPIView):
    """View for retrieve, update and remove taxi fare."""

    queryset = TaxiFare.objects.all()
    serializer_class = TaxiFareSerializer
    permission_classes = [IsAuthenticatedAdmin]
    authentication_classes = [AdminJWTAuthentication]


class TaxiFareListView(ListAPIView):
    """View taxi fare list."""

    queryset = TaxiFare.objects.all()
    serializer_class = TaxiFareSerializer
    permission_classes = [IsAuthenticatedAdmin]
    authentication_classes = [AdminJWTAuthentication]

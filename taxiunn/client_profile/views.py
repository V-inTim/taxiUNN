from rest_framework.response import Response
from rest_framework import generics
from client_auth.authentication import (
    IsAuthenticatedClient,
    ClientJWTAuthentication,
)
from client_auth.models import Client

from .serializers import (
    UpdateClientSerializer,
    ReceiveClientSerializer,
)


class ClientView(generics.RetrieveUpdateAPIView):
    """View клиентских данных."""

    queryset = Client.objects.all()
    permission_classes = [IsAuthenticatedClient]
    authentication_classes = [ClientJWTAuthentication]

    def retrieve(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = ReceiveClientSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = UpdateClientSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

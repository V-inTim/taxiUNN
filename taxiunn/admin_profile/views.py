from rest_framework import generics
from admin_auth.models import Admin

from .serializers import ReceiveAdminSerializer, UpdateAdminSerializer
from rest_framework.response import Response
from admin_auth.authentication import (
    IsAuthenticatedAdmin,
    AdminJWTAuthentication,
)


class AdminView(generics.RetrieveUpdateAPIView):
    """Данные админа."""

    queryset = Admin.objects.all()
    permission_classes = [IsAuthenticatedAdmin]
    authentication_classes = [AdminJWTAuthentication]

    def retrieve(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = ReceiveAdminSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = UpdateAdminSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

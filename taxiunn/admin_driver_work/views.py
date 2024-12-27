from smtplib import SMTPException

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from admin_auth.authentication import (
    AdminJWTAuthentication,
    IsAuthenticatedAdmin,
)
from admin_auth.password import make_password

from .message_service import send_password
from .serializers import DriverSerializer


class RegisterView(APIView):
    """View регистрации администратора."""

    permission_classes = [IsAuthenticatedAdmin]
    authentication_classes = [AdminJWTAuthentication]

    def post(self, request):
        serializer = DriverSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = make_password()
            try:
                serializer.save(password)
                send_password(
                    email=email,
                    password=password,
                )
            except SMTPException:
                return Response(
                    {'email': ['The email not found.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {'message': ['User successfully registered.']},
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

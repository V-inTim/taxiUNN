from smtplib import SMTPException

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import (
    DriverRegisterSerializer,
    DriverVerifyRegisterSerializer,
)

from taxiunn.verification import (
    RegistrationCache,
    make_verification_code,
    send_verification_code,
)


class RegistrationView(APIView):
    """View регистрации водителя."""

    def post(self, request) -> Response:
        serializer = DriverRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        verification_code = make_verification_code()

        RegistrationCache.save(
            email=email,
            code=verification_code,
            data=serializer.validated_data,
        )

        try:
            send_verification_code(
                email=email,
                verification_code=verification_code,
            )
        except SMTPException:
            return Response(
                {'message': 'Email not found!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'message': "You\'ve successfully registered!"},
            status=status.HTTP_200_OK,
        )


class VerificationOfRegistrationView(APIView):
    """View верификации регистрации водителя."""

    def post(self, request) -> Response:
        serializer = DriverVerifyRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        verification_code = serializer.validated_data['verification_code']

        data = RegistrationCache.verify(email=email, code=verification_code)

        if not data:
            return Response(
                {'message': 'Incorrect verification code!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DriverRegisterSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'message': "You\'ve successfully registered!"},
            status=status.HTTP_200_OK,
        )

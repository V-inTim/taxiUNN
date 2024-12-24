from smtplib import SMTPException

from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    RefreshSerializer,
    PasswordRecoverySerializer,
    AdminPasswordRecoveryVerifySerializer,
    AdminPasswordRecoveryChangeSerializer,
)

from taxiunn.verification import (
    make_verification_code,
    send_verification_code,
    PasswordRecoveryCache,
)


class LoginView(APIView):
    """View авторизации."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {'refresh': str(refresh), 'access': str(refresh.access_token)},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"password": ["Invalid credentials."]},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RefreshView(APIView):
    """Получение access_token по refresh_token."""

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh = serializer.validated_data.get('refresh')
        try:
            refresh = RefreshToken(refresh)
            return Response(
                {'access': str(refresh.access_token)},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"refresh": ['Refresh code is not active.']},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordRecoveryView(APIView):
    """View восстановления пароля для администратора."""

    def post(self, request) -> Response:
        serializer = PasswordRecoverySerializer(data=request.data)

        if serializer.is_valid():
            verification_code = make_verification_code()
            email = serializer.validated_data['email']

            PasswordRecoveryCache.save(
                email=email,
                code=verification_code,
            )

            try:
                send_verification_code(
                    email=email,
                    verification_code=verification_code,
                )
                return Response(
                    {'message': 'Check your email for the verification_code.'},
                    status=status.HTTP_200_OK,
                )
            except SMTPException:
                return Response(
                    {'email': ['The email not found.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordRecoveryVerifyView(APIView):
    """View верификации восстановления пароля для администратора."""

    def post(self, request) -> Response:
        serializer = AdminPasswordRecoveryVerifySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            verify_code = serializer.validated_data['verification_code']

            if PasswordRecoveryCache.verify(email=email, code=verify_code):
                return Response(
                    {'message': ['Verification was successful.']},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    'verification_code':
                        ['The verification code is not active.'],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordRecoveryChangeView(APIView):
    """View смены пароля и сохранения нового пароля для администратора."""

    def post(self, request) -> Response:
        serializer = AdminPasswordRecoveryChangeSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            if PasswordRecoveryCache.check(email=email):
                serializer.save()
                return Response(
                    {'message': ['Password successfully changed.']},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {'email': ['Something went wrong.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

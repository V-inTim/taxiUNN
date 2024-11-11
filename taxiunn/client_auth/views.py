from smtplib import SMTPException

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    PasswordRecoveryChangeSerializer,
    PasswordRecoverySerializer,
    PasswordRecoveryVerifySerializer,
    RegisterVerifySerializer,
)
from .verification import (
    PasswordRecoveryCache,
    RegistrationCache,
    make_verification_code,
    send_verification_code,
)


class RegisterView(APIView):
    """View регистрации."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        code = make_verification_code()

        # запись данных в Redis
        RegistrationCache.save(email=email, code=code)

        # Отправка кода на почту
        try:
            send_verification_code(email=email, verification_code=code)
            return Response(
                {'message': 'Check your email for the verification code.'},
                status=status.HTTP_200_OK,
            )
        except SMTPException:
            return Response(
                {'email': ['The email not found.']},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterVerifyView(APIView):
    """View верификации при регистрации и сохранения аккаунта."""

    def post(self, request):
        serializer = RegisterVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        code = serializer.validated_data['verification_code']

        data = RegistrationCache.verify(email=email, code=code)
        if not data:
            return Response(
                {'verification_code': ['Incorrect verification code.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        return Response(
            {'message': 'You have successfully registered.'},
            status=status.HTTP_200_OK,
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
    """View получения refresh токена."""

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(
                {'refresh': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh_token)
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
    """View восстановления пароля."""

    def post(self, request):
        serializer = PasswordRecoverySerializer(data=request.data)

        if serializer.is_valid():
            code = make_verification_code()
            email = serializer.validated_data['email']
            # запись данных в Redis
            PasswordRecoveryCache.save(email=email, code=code)

            # Отправка кода на почту
            try:
                send_verification_code(
                    email=email,
                    verification_code=code,
                )
                return Response(
                    {'message': 'Check your email for the verification code.'},
                    status=status.HTTP_200_OK,
                )
            except SMTPException:
                return Response(
                    {'email': ['The email not found.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordRecoveryVerifyView(APIView):
    """View верификации при восстановлении пароля."""

    def post(self, request):
        serializer = PasswordRecoveryVerifySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['verification_code']

            if PasswordRecoveryCache.verify(email=email, code=code):
                return Response(
                    {'message': 'Verification was successful.'},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    'verification_code': [
                        'The verification code is not active.',
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordRecoveryChangeView(APIView):
    """View изменения пароля."""

    def post(self, request):
        serializer = PasswordRecoveryChangeSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            if PasswordRecoveryCache.check(email=email):
                serializer.save()
                return Response(
                    {'message': 'Password changed.'},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {'email': ['Try again.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

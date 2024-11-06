from rest_framework.views import APIView
from smtplib import SMTPException

from .serializers import (
    ClientSerializer,
    PasswordRecoverySerializer,
    PasswordRecoveryVerifySerializer,
    PasswordRecoveryChangeSerializer,
)

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .verification import (
    send_verification_code,
    make_verification_code,
    PasswordRecoveryCache,
)


class RegisterView(APIView):
    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = make_verification_code()

            # запись данных в Redis
            cache.set(f'verification_code_{email}', code, timeout=3600)
            cache.set(f'user_data_{email}',
                      serializer.validated_data, timeout=3600)

            # Отправка кода на почту
            try:
                send_verification_code(email=email, verification_code=code)
                return Response({'message': ('Check your email for '
                                             'the verification code.')},
                                status=status.HTTP_200_OK)
            except SMTPException:
                return Response({'error': 'The email not found.'},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateView(APIView):
    def post(self, request):
        data = request.data
        if "email" not in data or "verification_code" not in data:
            return Response({'error': 'Missing parameters.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user_data = cache.get(f'user_data_{data["email"]}')
        code = cache.get(f'verification_code_{data["email"]}')

        if str(code) != data["verification_code"]:
            return Response({'error': 'Incorrect verification code.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ClientSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'You have successfully registered.'},
                        status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Missing parameters.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials."},
                        status=status.HTTP_400_BAD_REQUEST)


class RefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Missing parameters.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryView(APIView):
    def post(self, request):
        serializer = PasswordRecoverySerializer(data=request.data)

        if serializer.is_valid():
            code = make_verification_code()
            email = serializer.validated_data['email']
            # запись данных в Redis
            PasswordRecoveryCache.save(email=email, code=code)

            # Отправка кода на почту
            try:
                send_verification_code(email=email,
                                       verification_code=code)
                return Response({'message': ('Check your email for '
                                'the verification code.')},
                                status=status.HTTP_200_OK)
            except SMTPException:
                return Response({'email': ['The email not found.']},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryVerifyView(APIView):
    def post(self, request):
        serializer = PasswordRecoveryVerifySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['verification_code']

            if PasswordRecoveryCache.verify(email=email, code=code):
                return Response({'message':
                                'Verification was successful.'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'verification_code':
                                ['The verification code is not active.']},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryChangeView(APIView):
    def post(self, request):
        serializer = PasswordRecoveryChangeSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            if PasswordRecoveryCache.check(email=email):
                serializer.save()
                return Response({'message': 'Password changed.'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'email': ['Try again.']},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

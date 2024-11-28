from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, RefreshSerializer


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

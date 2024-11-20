from rest_framework import serializers

from .models import Admin


class LoginSerializer(serializers.ModelSerializer):
    """Сериалайзер авторизации."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Admin
        fields = ['email', 'password']

    def validate_email(self, value: str):
        """Проверка существования модели с таким email."""
        if not Admin.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email does not exist.",
            )
        return value


class RefreshSerializer(serializers.Serializer):
    """Сериалайзер Refresh-токена."""

    refresh = serializers.CharField(write_only=True)

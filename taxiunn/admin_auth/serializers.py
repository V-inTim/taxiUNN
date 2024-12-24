from typing import Optional

from rest_framework import serializers

from .models import Admin


class LoginSerializer(serializers.ModelSerializer):
    """Сериалайзер авторизации."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Admin
        fields = ['email', 'password']

    def validate_email(self, value: str) -> str:
        """Проверка существования модели с таким email."""
        if not Admin.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email does not exist.",
            )
        return value


class RefreshSerializer(serializers.Serializer):
    """Сериалайзер Refresh-токена."""

    refresh = serializers.CharField(write_only=True)


class PasswordRecoverySerializer(serializers.ModelSerializer):
    """Сериалайзер восстановления пароля для администратора."""

    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Admin
        fields = ['email']

    def validate_email(self, value: str) -> Optional[str]:
        """Валидация email (что пользователь с таким email существует)."""
        if not Admin.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email does not exist.",
            )
        return value


class AdminPasswordRecoveryVerifySerializer(PasswordRecoverySerializer):
    """Сериалайзер верификации восстановления пароля для администратора."""

    verification_code = serializers.CharField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        fields = PasswordRecoverySerializer.Meta.fields + ['verification_code']


class AdminPasswordRecoveryChangeSerializer(PasswordRecoverySerializer):
    """Сериалайзер изменения пароля администратора."""

    password = serializers.CharField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        fields = PasswordRecoverySerializer.Meta.fields + ['password']

    def save(self) -> Admin:
        """Метод сохранения нового пароля."""
        user = Admin.objects.get(
            email=self.validated_data.get('email'),
        )

        user.set_password(
            self.validated_data['password'],
        )

        user.save()
        return user

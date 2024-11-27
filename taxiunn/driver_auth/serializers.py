from rest_framework import serializers

from .models import Driver


class BaseDriverSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер для водителя."""

    email = serializers.EmailField(write_only=True)

    def validate_email(self, value: str):
        """Валидация email (что пользователь с таким email ещё не создан)."""
        if Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exist!",
            )
        return value


class DriverRegisterSerializer(BaseDriverSerializer):
    """Сериалайзер для регистрации водителя."""

    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email', 'password', 'full_name']

    def create(self, validated_data):
        """Создание объекта класса Driver."""
        user = Driver.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
        )
        return user


class DriverVerifyRegisterSerializer(serializers.ModelSerializer):
    """Сериалайзер для верификации регистрации водителя."""

    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email', 'verification_code']

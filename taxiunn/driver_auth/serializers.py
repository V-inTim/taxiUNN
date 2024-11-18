from rest_framework import serializers

from .models import Driver


class DriverRegisterSerializer(serializers.ModelSerializer):
    """ Сериалайзер для регистрации водителя """

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email', 'password']

    def validate_email(self, value: str):
        """ Валидация email (что пользователь с таким email ещё не создан) """
        if Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exist!",
            )
        return value

    def create(self, validated_data):
        """ Создание объекта класса Driver """
        user = Driver.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class DriverVerifyRegisterSerializer(serializers.ModelSerializer):
    """ Сериалайзер для верификации регистрации водителя """

    email = serializers.EmailField(write_only=True)
    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email', 'verification_code']

    def validate_email(self, value: str):
        """ Валидация email (что пользователь с таким email ещё не создан) """
        if Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exist!",
            )
        return value

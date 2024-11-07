from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """ Используется для преобразования данных в объект Client """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = ['email', 'password']

    def create(self, validated_data):
        user = Client.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class PasswordRecoverySerializer(serializers.ModelSerializer):

    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Client
        fields = ['email']

    def validate_email(self, value: str):
        # Проверка существования модели с таким email
        if not Client.objects.filter(email=value).exists():
            raise serializers.ValidationError(("An account with "
                                               "this email does not exist."))

        return value


class PasswordRecoveryVerifySerializer(PasswordRecoverySerializer):

    verification_code = serializers.IntegerField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        fields = PasswordRecoverySerializer.Meta.fields + ['verification_code']


class PasswordRecoveryChangeSerializer(PasswordRecoverySerializer):

    password = serializers.CharField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        fields = PasswordRecoverySerializer.Meta.fields + ['password']

    def save(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')

        user = Client.objects.get(email=email)
        user.set_password(password)

        user.save()
        return user

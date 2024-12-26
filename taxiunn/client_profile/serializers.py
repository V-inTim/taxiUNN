from rest_framework import serializers

from client_auth.models import Client


class ReceiveClientSerializer(serializers.ModelSerializer):
    """Сериалайзер для администратора."""

    class Meta:
        model = Client
        fields = ['email', 'full_name', 'bank_balance']


class UpdateClientSerializer(serializers.ModelSerializer):
    """Сериалайзер для администратора."""

    class Meta:
        model = Client
        fields = ['full_name']

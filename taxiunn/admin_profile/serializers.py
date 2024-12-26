from rest_framework import serializers

from admin_auth.models import Admin


class ReceiveAdminSerializer(serializers.ModelSerializer):
    """Сериалайзер для администратора."""

    class Meta:
        model = Admin
        fields = ['email', 'full_name']


class UpdateAdminSerializer(serializers.ModelSerializer):
    """Сериалайзер для администратора."""

    class Meta:
        model = Admin
        fields = ['full_name']

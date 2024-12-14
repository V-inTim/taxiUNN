from rest_framework import serializers

from .message import DriverOrderStatus, ClientOrderStatus


class DriverMessageSerializer(serializers.Serializer):
    """Сериалайзер сообщений водителя."""

    message_type = serializers.CharField(write_only=True)

    def validate_message_type(self, value: str):
        """Проверка типа сообщения."""
        if not DriverOrderStatus.is_valid(value):
            raise serializers.ValidationError(
                "Unexpected message type.",
            )
        return value


class ClientMessageSerializer(serializers.Serializer):
    """Сериалайзер сообщений клиента."""

    message_type = serializers.CharField(write_only=True)
    info = serializers.DictField(write_only=True)

    def validate_message_type(self, value: str):
        """Проверка типа сообщения."""
        if not ClientOrderStatus.is_valid(value):
            raise serializers.ValidationError(
                "Unexpected message type.",
            )
        return value


class OrderSerializer(serializers.Serializer):
    """Сериалайзер заказа."""

    location_from = serializers.ListSerializer(write_only=True)
    location_to = serializers.ListSerializer(write_only=True)
    fare = serializers.CharField(write_only=True)
    price = serializers.FloatField(write_only=True)

    def validate_location_from(self, value: tuple):
        """Проверка координат отправки."""
        if len(value) != 2:
            raise serializers.ValidationError(
                "Incorrect format of coordinates.",
            )
        return value

    def validate_location_to(self, value: tuple):
        """Проверка координат места назначения."""
        if len(value) != 2:
            raise serializers.ValidationError(
                "Incorrect format of coordinates.",
            )
        return value

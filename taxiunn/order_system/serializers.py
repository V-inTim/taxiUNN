from rest_framework import serializers

from .message import MessageType


class DriverMessageSerializer(serializers.Serializer):
    """Сериалайзер сообщений водителя."""

    message_type = serializers.CharField(write_only=True)
    info = serializers.DictField(required=False)

    def validate_message_type(self, value: str):
        """Проверка типа сообщения."""
        if not MessageType.is_valid_for_driver(value):
            raise serializers.ValidationError(
                "Unexpected message type.",
            )
        return value

    def validate(self, data):
        """Проверка всех данных сериализатора."""
        message_type = data.get('message_type')
        info = data.get('info', {})

        if (
            message_type and
            message_type in {
                MessageType.FIND_ORDER.value,
                MessageType.POSSIBLE_ORDER.value,
            } and
            not info
        ):
            raise serializers.ValidationError(
                "Info field is required.",
            )

        return data


class ClientMessageSerializer(serializers.Serializer):
    """Сериалайзер сообщений клиента."""

    message_type = serializers.CharField(write_only=True)
    info = serializers.DictField(required=False)

    def validate_message_type(self, value: str):
        """Проверка типа сообщения."""
        if not MessageType.is_valid_for_client(value):
            raise serializers.ValidationError(
                "Unexpected message type.",
            )
        return value

    def validate(self, data):
        """Проверка всех данных сериализатора."""
        message_type = data.get('message_type')
        info = data.get('info', {})

        if (
            message_type and
            message_type == MessageType.MAKE_ORDER and
            not info
        ):
            raise serializers.ValidationError(
                "Info field is required.",
            )

        return data


class OrderSerializer(serializers.Serializer):
    """Сериалайзер заказа."""

    location_from = serializers.ListSerializer(
        child=serializers.FloatField(),
        write_only=True,
    )
    location_to = serializers.ListSerializer(
        child=serializers.FloatField(),
        write_only=True,
    )
    fare = serializers.CharField(write_only=True)
    price = serializers.DecimalField(
        write_only=True,
        max_digits=10,
        decimal_places=2,
    )

    def validate_location_from(self, value: list):
        """Проверка координат отправки."""
        if len(value) != 2:
            raise serializers.ValidationError(
                "Incorrect format of coordinates.",
            )
        return value

    def validate_location_to(self, value: list):
        """Проверка координат места назначения."""
        if len(value) != 2:
            raise serializers.ValidationError(
                "Incorrect format of coordinates.",
            )
        return value


class DriverSerializer(serializers.Serializer):
    """Сериалайзер водительских данных."""

    location = serializers.ListSerializer(
        child=serializers.FloatField(),
        write_only=True,
    )

    def validate_location(self, value: list):
        """Проверка координат отправки."""
        if len(value) != 2:
            raise serializers.ValidationError(
                "Incorrect format of coordinates.",
            )
        return value


class AnswerSerializer(serializers.Serializer):
    """Сериалайзер водительского ответа."""

    is_agree = serializers.BooleanField(required=True)


class CoordinateSerializer(serializers.Serializer):
    """Сериалайзер списка координат."""

    location_from = serializers.ListField(
        child=serializers.FloatField(),
        min_length=2,
        max_length=2,
    )
    location_to = serializers.ListField(
        child=serializers.FloatField(),
        min_length=2,
        max_length=2,
    )

    def validate_location_from(self, value: list):
        """Проверка координаты."""
        if len(value) != 2:
            raise serializers.ValidationError(
                "coord1 must contain exactly 2 float values.",
            )
        return value

    def validate_location_to(self, value: list):
        """Проверка координаты."""
        if len(value) != 2:
            raise serializers.ValidationError(
                "coord2 must contain exactly 2 float values.",
            )
        return value

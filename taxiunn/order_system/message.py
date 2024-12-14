from enum import Enum


class TripStatus(Enum):
    """Статус поездки."""

    DRIVER_ON_SITE = 'DRIVER_ON_SITE'
    TRIP_BEGINNIG = 'TRIP_BEGINNIG'
    TRIP_ENDING = 'TRIP_ENDING'


class DriverOrderStatus(TripStatus):
    """Водительский статус заказа."""

    FIND_ORDER = 'FIND_ORDER'
    POSSIBLE_ORDER = 'POSSIBLE_ORDER'
    ACCEPT_ORDER = 'ACCEPT_ORDER'

    @classmethod
    def is_valid(cls, value):
        """Проверка значения."""
        return value in cls.__members__.values()


class ClientOrderStatus(TripStatus):
    """Клиентский статус заказа."""

    MAKE_ORDER = 'MAKE_ORDER'
    DRIVER_FOUND = 'DRIVER_FOUND'

    @classmethod
    def is_valid(cls, value):
        """Проверка значения."""
        return value in cls.__members__.values()


class Message:
    """Класс сообщения."""

    def __init__(self, message_type: str, info: dict):
        """Конструктор."""
        self.message_type = message_type
        self.info = info
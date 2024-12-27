from enum import Enum


class MessageType(Enum):
    """Тип сообщения."""

    MAKE_ORDER = 'MAKE_ORDER'
    DRIVER_DATA = 'DRIVER_DATA'

    FIND_ORDER = 'FIND_ORDER'
    CANCEL = 'CANCEL'

    POSSIBLE_ORDER = "POSSIBLE_ORDER"
    NOT_CURRENT_ORDER = "NOT_CURRENT_ORDER"
    DRIVER_ON_THE_WAY = 'DRIVER_ON_THE_WAY'
    DRIVER_ON_SITE = 'DRIVER_ON_SITE'
    TRIP_BEGINNING = 'TRIP_BEGINNING'
    TRIP_ENDING = 'TRIP_ENDING'

    ERROR = 'ERROR'

    @classmethod
    def is_valid_for_client(cls, value):
        """Проверка значения."""
        return value in {cls.MAKE_ORDER.value, cls.CANCEL.value}

    @classmethod
    def is_valid_for_driver(cls, value):
        """Проверка значения."""
        return value in {
            cls.FIND_ORDER.value,
            cls.CANCEL.value,
            cls.POSSIBLE_ORDER.value,
            cls.DRIVER_ON_SITE.value,
            cls.TRIP_BEGINNING.value,
            cls.TRIP_ENDING.value,
        }


class Message:
    """Класс сообщения."""

    def __init__(self, message_type: str, info: dict = None):
        """Конструктор."""
        self._message_type = message_type
        self._info = info

    @property
    def message_type(self):
        """Getter."""
        return self._message_type

    @property
    def info(self):
        """Getter."""
        return self._info

    @message_type.setter
    def message_type(self, message_type: str):
        """Setter."""
        self._message_type = message_type

    @info.setter
    def info(self, info: dict):
        """Setter."""
        self._info = info

    def to_dict(self):
        """Get dict."""
        response = {'message_type': self._message_type}
        if self._info:
            response.update({'info': self._info})
        return response

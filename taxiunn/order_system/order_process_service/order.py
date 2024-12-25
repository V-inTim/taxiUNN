from enum import Enum


class OrderStatus(Enum):
    """Статус заказа."""

    NONE = 0
    DRIVER_ON_THE_WAY = 1
    DRIVER_ON_SITE = 2
    TRIP_BEGINNING = 3
    TRIP_ENDING = 4


class Order:
    """Класс заказа."""

    def __init__(
        self,
        location_from: list,
        location_to: list,
        fare: str,
        price: float,
    ):
        """Конструктор."""
        self._location_from = location_from
        self._location_to = location_to
        self._fare = fare
        self._price = price

    @property
    def fare(self):
        """Getter."""
        return self._fare

    @property
    def price(self):
        """Getter."""
        return self._price

    @property
    def location_from(self):
        """Getter."""
        return self._location_from

    @property
    def location_to(self):
        """Getter."""
        return self._location_to

    @fare.setter
    def fare(self, fare: str):
        """Setter."""
        self._fare = fare

    @price.setter
    def price(self, price: float):
        """Setter."""
        self._price = price

    @location_from.setter
    def location_from(self, location_from: list):
        """Setter."""
        self._location_from = location_from

    @location_to.setter
    def location_to(self, location_to: list):
        """Setter."""
        self._location_to = location_to

    def to_dict(self):
        """Json."""
        return {
            'fare': self._fare,
            'price': str(self._price),
            'location_from': self._location_from,
            'location_to': self._location_to,
        }

    def executor_data(self):
        """Json."""
        return {
            'fare': self._fare,
            'location_from': self._location_from,
            'location_to': self._location_to,
        }

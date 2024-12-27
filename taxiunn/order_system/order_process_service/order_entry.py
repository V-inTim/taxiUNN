from datetime import datetime

from .order import Order


class OrderEntry(Order):
    """Запись заказа."""

    _time_order_start: str
    _time_trip_beginning: str
    _time_trip_ending: str

    def __init__(self, order: Order = None):
        """Конструктор."""
        if order:
            super().__init__(
                order.location_from,
                order.location_to,
                order.fare,
                order.price,
            )

        self._time_order_start = None
        self._time_trip_beginning = None
        self._time_trip_ending = None

    def make_time_order_start(self):
        """Setter."""
        now = datetime.now()
        self._time_order_start = now.strftime("%Y-%m-%d %H:%M")

    def make_time_trip_beginning(self):
        """Setter."""
        now = datetime.now()
        self._time_trip_beginning = now.strftime("%Y-%m-%d %H:%M")

    def make_time_trip_ending(self):
        """Setter."""
        now = datetime.now()
        self._time_trip_ending = now.strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        """Get dict."""
        order_entry = {
            'time_order_start': self._time_order_start,
            'time_trip_beginning': self._time_trip_beginning,
            'time_trip_ending': self._time_trip_ending,
        }
        order_entry.update(super().to_dict())
        return order_entry

    @property
    def time_order_start(self):
        """Getter."""
        return self._time_order_start

    @property
    def time_trip_beginning(self):
        """Getter."""
        return self._time_trip_beginning

    @property
    def time_trip_ending(self):
        """Getter."""
        return self._time_trip_ending

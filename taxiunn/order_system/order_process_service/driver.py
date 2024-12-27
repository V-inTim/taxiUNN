NUM_POSSIBLE = 3


class Driver:
    """Driver data."""

    def __init__(self):
        """Конструктор."""
        self._num_possible = 0
        self._location = None
        self._is_work_beginning = False
        self._unsuitable_orders = set()

    @property
    def location(self):
        """Getter."""
        return self._location

    @location.setter
    def location(self, location: list):
        """Setter."""
        self._location = location

    def is_possible(self):
        """Можно ли попросить другой заказ."""
        self._num_possible += 1
        return self._num_possible <= NUM_POSSIBLE

    @property
    def is_work_beginning(self):
        """Getter."""
        return self._is_work_beginning

    @is_work_beginning.setter
    def is_work_beginning(self, is_work_beginning):
        self._is_work_beginning = is_work_beginning

    def add_unsuitable_order(self, order_id: str):
        """Add suitable order."""
        self._unsuitable_orders.add(order_id)

    @property
    def unsuitable_orders(self):
        """Getter."""
        return self._unsuitable_orders

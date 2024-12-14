import redis
from geopy.distance import geodesic

from taxiunn.settings import REDIS_HOST, REDIS_PASSWORD


class Order:
    """Класс заказа."""

    def __init__(
        self,
        location_from: tuple,
        location_to: tuple,
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


class OrderManager:
    """Менеджер заказов."""

    def __init__(self):
        """Конструктор."""
        self.storage = redis.Redis(
            host=REDIS_HOST,
            port=6379,
            db=0,
            password=REDIS_PASSWORD,
        )

    def add(self, order: Order, order_id):
        """Добавить заказ в хранилище."""
        self.storage.sadd("order_ids", order_id)
        entry = {'order': order, 'executor': None}
        self.storage.hset(f'client_order_{order_id}', mapping=entry)

    def remove(self, order_id):
        """Удалить заказ из хранилища."""
        self.storage.srem(order_id)
        self.storage.hdel(f'client_order_{order_id}')

    def find_nearest(self, executor_id, executor_location):
        """Найти ближайший заказ."""
        order_ids = list(self.storage.smembers("order_ids"))

        if not len(order_ids):
            return None

        min_distance = 5
        optimal_order = None
        optimal_order_id = None

        for order_id in order_ids:
            entry: dict = self.storage.hget(f'client_order_{order_id}')

            if entry.get('executor'):
                continue

            order = entry.get('order')
            distance = self._calc_distance(
                order.location_from,
                executor_location,
            )
            if min_distance > distance:
                if optimal_order_id:
                    self.free(optimal_order_id)
                self._stake_out(order_id, executor_id, entry)

                min_distance = distance
                optimal_order = order
                optimal_order_id = order_id

        return optimal_order, optimal_order_id

    def free(self, order_id):
        """Освободить заказ."""
        entry = self.storage.hget(f'client_order_{order_id}')
        entry['executor'] = None
        self.storage.hset(f'client_order_{order_id}', entry)

    def _calc_distance(self, order_location, executor_location):
        """Найти расстояние."""
        return geodesic(executor_location, order_location).kilometers

    def _stake_out(self, order_id, executor_id, entry):
        """Застолбить заказ."""
        entry['executor'] = executor_id
        self.storage.hset(f'client_order_{order_id}', entry)

import json
import functools
import asyncio

import redis
from geopy.distance import geodesic

from taxiunn.settings import REDIS_HOST, REDIS_PASSWORD

from .order import OrderStatus, Order
from .order_entry import OrderEntry

# для inactive
MIN_DISTANCE = 3
NONE = 0

NUMBER_OF_ATTEMPTS = 10
DELAY = 60


def retry(attempts: int, delay: int):
    """Retry action."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < attempts:
                result = await func(*args, **kwargs)
                if result:
                    return result
                attempt += 1
                await asyncio.sleep(delay)
            return None
        return wrapper
    return decorator


class InactiveOrderManager:
    """Менеджер заказов."""

    def __init__(self):
        """Конструктор."""
        self.storage = redis.Redis(
            host=REDIS_HOST,
            port=6379,
            db=1,
            password=REDIS_PASSWORD,
        )

    def add(self, order: Order, order_id: str):
        """Добавить заказ в хранилище."""
        self.storage.sadd('order_ids', order_id)
        entry = {'order': order.to_dict(), 'executor': NONE}
        self.storage.hset(
            'client_orders',
            key=order_id,
            value=json.dumps(entry),
        )

    def remove(self, order_id: str):
        """Удалить заказ из хранилища."""
        self.storage.srem('order_ids', order_id)
        self.storage.hdel('client_orders', order_id)

    @retry(attempts=NUMBER_OF_ATTEMPTS, delay=DELAY)
    async def get_nearest(
        self,
        executor_id: str,
        executor_location: list,
        unsuitable_orders: set,
    ):
        """Найти ближайший заказ."""
        order_ids = self.storage.smembers("order_ids")
        if not len(order_ids):
            return None
        encoded_set = {value.encode('utf-8') for value in unsuitable_orders}

        order_ids = list(order_ids.difference(encoded_set))

        optimal_order, optimal_order_id = self._find_optimal_order(
            order_ids,
            executor_id,
            executor_location,
        )

        if not optimal_order_id:
            return None
        return optimal_order, optimal_order_id

    def free(self, order_id: str):
        """Освободить заказ."""
        entry = json.loads(self.storage.hget('client_orders', order_id))
        entry['executor'] = NONE
        self.storage.hset('client_orders', order_id, json.dumps(entry))

    def _find_optimal_order(
        self,
        order_ids: list,
        executor_id: str,
        executor_location: list,
    ):
        """Найти оптимальный заказ."""
        min_distance = MIN_DISTANCE
        optimal_order = None
        optimal_order_id = None

        for order_id in order_ids:
            entry: dict = json.loads(self.storage.hget(
                'client_orders',
                order_id,
            ))

            if entry.get('executor'):
                continue

            order = Order(**entry.get('order'))
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
                optimal_order_id = order_id.decode('utf-8')
        return optimal_order, optimal_order_id

    def _calc_distance(self, order_location: list, executor_location: list):
        """Найти расстояние."""
        return geodesic(executor_location, order_location).kilometers

    def _stake_out(self, order_id: str, executor_id: str, entry: dict):
        """Застолбить заказ."""
        entry['executor'] = executor_id
        self.storage.hset('client_orders', order_id, json.dumps(entry))


class ActiveOrderManager:
    """Класс обслуживания заказов."""

    _order_status: OrderStatus
    _order_entry: OrderEntry

    def __init__(self, order: Order = None):
        """Конструктор."""
        self._order_status = OrderStatus.NONE
        self._order_entry = OrderEntry(order)

    async def is_possiple_to_cancel(self):
        """Проверить можно ли отменить заказ."""
        return self._order_status.value <= OrderStatus.DRIVER_ON_SITE.value

    async def change_status(self, order_status: OrderStatus):
        """Изменить статус."""
        if order_status.value != self._order_status.value + 1:
            return False
        self._order_status = order_status
        await self._make_timestamp(order_status)
        return True

    async def _make_timestamp(self, order_status: OrderStatus):
        if order_status == OrderStatus.DRIVER_ON_THE_WAY:
            self._order_entry.make_time_order_start()
        elif order_status == OrderStatus.TRIP_BEGINNING:
            self._order_entry.make_time_trip_beginning()
        elif order_status == OrderStatus.TRIP_ENDING:
            self._order_entry.make_time_trip_ending()

    @property
    def order_status(self):
        """Getter."""
        return self._order_status

    @property
    def order_entry(self):
        """Getter."""
        return self._order_entry

    @order_status.setter
    def order_status(self, order_status: OrderStatus):
        """Setter."""
        self._order_status = order_status

    @order_entry.setter
    def order_entry(self, order_entry: OrderEntry):
        """Setter."""
        self._order_entry = order_entry

    def timestamp(self):
        """Get Time."""
        if self.order_status == OrderStatus.DRIVER_ON_THE_WAY:
            return {
                'time_order_start': self.order_entry.time_order_start,
            }
        elif self.order_status == OrderStatus.DRIVER_ON_SITE:
            return {}
        elif self.order_status == OrderStatus.TRIP_BEGINNING:
            return {
                'time_trip_beginning': self.order_entry.time_trip_beginning,
            }
        elif self.order_status == OrderStatus.TRIP_ENDING:
            return {
                'time_trip_ending': self.order_entry.time_trip_ending,
            }

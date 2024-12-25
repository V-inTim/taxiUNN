import json

import redis

from taxiunn.settings import REDIS_HOST, REDIS_PASSWORD

TIME_LIFE_RPICE = 600


class PriceManager:
    """Менеджер хранимых данных о стоимоятх заказов."""

    @classmethod
    def set(cls, email: str, price_list: list):
        """Устaновить price list."""
        client = redis.StrictRedis(
            host=REDIS_HOST,
            port=6379,
            db=2,
            password=REDIS_PASSWORD,
        )

        key = f'order_price{email}'
        value = json.dumps(price_list)
        client.set(key, value, ex=TIME_LIFE_RPICE)

    @classmethod
    def check(cls, email: str, fare: str, price) -> bool:
        """Проверить хранимые значения."""
        client = redis.StrictRedis(
            host=REDIS_HOST,
            port=6379,
            db=2,
            password=REDIS_PASSWORD,
        )

        key = f'order_price{email}'
        value = client.get(key)
        if not value:
            return False
        price_list = json.loads(value)

        for entry in price_list:
            if entry['name'] == fare:
                return entry['price'] == str(price)

        return False

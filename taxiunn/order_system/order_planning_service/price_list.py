from decimal import Decimal, ROUND_HALF_UP

from taxi_fare.fare_service import get_fare_list

from .map_client import get_time


def get_price_list(location_from: list, location_to: list):
    """Дает список цен по тарифам."""
    fare_list = get_fare_list()
    price_list = []
    time = Decimal(get_time(location_from, location_to))
    time = time.quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
    for fare in fare_list:
        order_price = fare['price'] * time
        order_price = order_price.quantize(
            Decimal("1.00"),
            rounding=ROUND_HALF_UP,
        )
        price_list.append({'name': fare['name'], 'price': str(order_price)})
    return price_list

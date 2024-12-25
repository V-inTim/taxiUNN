from .models import TaxiFare


def get_fare_list() -> list:
    """Дает список тарифов."""
    fares = TaxiFare.objects.all()
    response = []
    for fare in fares:
        response.append({'name': fare.name, 'price': fare.price})

    return response

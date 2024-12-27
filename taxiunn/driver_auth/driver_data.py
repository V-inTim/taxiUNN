from asgiref.sync import sync_to_async

from .models import Driver


@sync_to_async
def get_driver_data(email: str):
    """Дать водительские данные."""
    user = Driver.objects.get(email=email)
    car = user.car
    if car:
        return {
            'model': car.model,
            'make': car.make,
            'color': car.color,
            'state_number': car.state_number,
        }
    return {}

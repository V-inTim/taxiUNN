import requests
import json

from taxiunn.settings import MAP_URL, MAP_TOKEN


TIMEOUT = 5


def get_time(location_from: list, location_to: list):
    """Дает время проезда между двумя точками."""
    data = {'locations': [location_from, location_to]}

    response = requests.post(
        MAP_URL,
        headers={
            'Authorization': 'Bearer ' + MAP_TOKEN,
            'Content-Type': 'application/json',
        },
        data=json.dumps(data),
        timeout=TIMEOUT,
    )
    if response.status_code != 200:
        raise Exception("Error when interacting with the service.")

    response_data = response.json()
    durations = response_data['durations']

    time_in_seconds = durations[0][1]
    time_in_hours = (time_in_seconds // 60) / 60
    return time_in_hours

from django.urls import re_path

from .consumers import ClientConsumer, DriverConsumer

websocket_urlpatterns = [
    re_path(r'ws/client$', ClientConsumer.as_asgi()),
    re_path(r'ws/driver$', DriverConsumer.as_asgi()),
]

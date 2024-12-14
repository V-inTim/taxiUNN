import json

from rest_framework.response import Response
from rest_framework import status
from channels.generic.websocket import AsyncWebsocketConsumer

from .serializers import ClientMessageSerializer
from .message import Message, ClientOrderStatus
from order_service import Order, OrderManager


class ClientConsumer(AsyncWebsocketConsumer):
    """Класс, обрабатывающий клиентское сокет-соединение."""

    async def connect(self):
        """Соединение."""
        await self.accept()

    async def receive(self, text_data):
        """Получение сообщение."""
        message = json.loads(text_data)
        serializer = ClientMessageSerializer(data=message)
        if not serializer.is_valid():
            message = Message(
                message_type='ERROR',
                info=serializer.errors,
            )
            await self.send(text_data=json.dumps(message))

        # message_type = serializer.validated_data['message_type']
        # info = serializer.validated_data['info']

    # async def message_process(self, message_type: str, info: dict):
    #     """Обработка сообщений клиента."""
    #     order_manager = OrderManager()
    #     if message_type == ClientOrderStatus.MAKE_ORDER:
            
    #         # order = Order()
    #         # order_manager.add()
    #         serializer 

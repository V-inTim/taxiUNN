import json
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer
from client_profile.bank_system import check_solvency, withdraw_amount

from .serializers import (
    ClientMessageSerializer,
    DriverMessageSerializer,
    OrderSerializer,
    DriverSerializer,
    AnswerSerializer,
)
from .message import MessageType, Message
from .order_process_service.order import Order, OrderStatus
from .order_process_service.order_manager import (
    InactiveOrderManager,
    ActiveOrderManager,
)
from .order_process_service.driver import Driver
from .order_planning_service.price_manager import PriceManager


class ClientConsumer(AsyncWebsocketConsumer):
    """Класс, обрабатывающий клиентское сокет-соединение."""

    inactive_order_manager: InactiveOrderManager
    active_order_manager: ActiveOrderManager

    async def connect(self):
        """Соединение."""
        self.is_order_active = False
        self.inactive_order_manager = InactiveOrderManager()
        self.active_order_manager = None
        self.group_name = f'group{uuid.uuid4().hex}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        await self.accept()

    async def receive(self, text_data):
        """Получение сообщение."""
        message = json.loads(text_data)
        serializer = ClientMessageSerializer(data=message)
        if serializer.is_valid():
            message = Message(**serializer.validated_data)
            await self.message_process(message)
        else:
            await self.send_error_message(serializer.errors)

    async def message_process(self, message: Message):
        """Обработка сообщений клиента."""
        if message.message_type == MessageType.MAKE_ORDER.value:
            serializer = OrderSerializer(data=message.info)
            if serializer.is_valid():
                order = Order(**serializer.validated_data)
                await self.check_order(order)
                self.inactive_order_manager.add(order, self.group_name)
                self.price = order.price
            else:
                await self.send_error_message(serializer.errors)
        elif message.message_type == MessageType.CANCEL.value:
            await self.cancel()

    async def check_order(self, order: Order):
        """Проверка заказа на актальность."""
        email = self.scope['user']
        if not PriceManager.check(email, order.fare, order.price):
            await self.send_error_message(
                {'error': ['The order price is not relevant.']},
            )
            await self.complete()
        elif not await check_solvency(email, order.price):
            await self.send_error_message(
                {'error': ['You are insolvent.']},
            )
            await self.complete()

    async def send_error_message(self, errors: dict):
        """Отправить сообщение с ошибками."""
        message = {
            'message_type': MessageType.ERROR.value,
            'info': errors,
        }
        await self.send(text_data=json.dumps(message))

    async def cancel(self):
        """Обработка сообщения отмены заказа."""
        if self.is_order_active:
            result = await self.active_order_manager.is_possiple_to_cancel()
            if result:
                message = {'message_type': MessageType.CANCEL.value}
                await self.channel_layer.group_send(
                    self.group_name,
                    {'type': 'chat_message', 'message': message},
                )
                self.complete()
            else:
                await self.send_error_message(
                    {'error': ['Inappropriate order status.']},
                )
        else:
            await self.complete()

    async def chat_message(self, event):
        """Сообщение от клиента."""
        message = event['message']
        message_type = message['message_type']

        if message_type == MessageType.CANCEL.value:
            await self.send(text_data=json.dumps(message))
            await self.complete()
        elif message_type == MessageType.DRIVER_DATA.value:
            self.active_order_manager = ActiveOrderManager()
            self.is_order_active = True
            await self.send(text_data=json.dumps(message))
        else:
            self.active_order_manager.change_status(
                OrderStatus[message_type],
            )
            await self.send(text_data=json.dumps(message))
            if message_type == MessageType.TRIP_ENDING.value:
                email = self.scope['user']
                await withdraw_amount(email, self.price)
                await self.complete()

    async def disconnect(self, close_code):
        """Автоматически при отсоединении."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        if not self.is_order_active:
            self.inactive_order_manager.remove(self.group_name)

    async def complete(self):
        """Автоматически при отсоединении."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        if not self.is_order_active:
            self.inactive_order_manager.remove(self.group_name)
        await self.close()

    # FIXME: change on async
    # FIXME: check entities of drive prices
    # FIXME: time limit of order


class DriverConsumer(AsyncWebsocketConsumer):
    """Класс, обрабатывающий водительское сокет-соединение."""

    async def connect(self):
        """Соединение."""
        self.is_order_active = False
        self.inactive_order_manager = InactiveOrderManager()
        self.active_order_manager = None
        self.group_name = None
        self.driver = Driver()
        await self.accept()

    async def receive(self, text_data):
        """Получение сообщение."""
        message = json.loads(text_data)
        serializer = DriverMessageSerializer(data=message)
        if serializer.is_valid():
            message = Message(**serializer.validated_data)
            await self.message_process(message)
        else:
            await self.send_error_message(serializer.errors)

    async def message_process(self, message: Message):
        """Обработка сообщений клиента."""
        if message.message_type == MessageType.FIND_ORDER.value:
            await self.check_driver(message.info)
            await self.find_order()
        elif message.message_type == MessageType.CANCEL.value:
            await self.cancel()
        elif message.message_type == MessageType.POSSIBLE_ORDER.value:
            if self.group_name and not self.is_order_active:
                await self.make_decision(message.info)
            else:
                await self.send_error_message(
                    {'error': ["Response without order offered."]},
                )
        else:
            await self.change_status(OrderStatus[message.message_type])

    async def find_order(self):
        """Найти заказ."""
        unsuitable_orders = self.driver.unsuitable_orders
        result = await self.inactive_order_manager.get_nearest(
            self.channel_name,
            self.driver.location,
            unsuitable_orders,
        )
        if result:
            order, order_id = result
            self.active_order_manager = ActiveOrderManager(order)
            self.group_name = order_id
            await self.send(json.dumps({
                'message_type': MessageType.POSSIBLE_ORDER.value,
                'info': order.executor_data(),
            }))
        else:
            await self.send_error_message(
                {'error': ['There are no active orders.']},
            )
            await self.complete()

    async def check_driver(self, message_info: dict):
        """Проверка данных вододителя."""
        if not self.driver.is_work_beginning:
            serializer = DriverSerializer(data=message_info)
            if serializer.is_valid():
                self.driver.is_work_beginning = True
                self.driver.location = serializer.validated_data['location']
            else:
                await self.send_error_message(serializer.errors)
        else:
            await self.send_error_message(
                {'error': ["Work has already begun."]},
            )

    async def change_status(self, status: OrderStatus):
        """Изменить статус заказа."""
        if await self.active_order_manager.change_status(status):
            result = self.active_order_manager.timestamp()
            message = {'message_type': status.name, 'info': result}
            response = {
                'type': 'chat_message',
                'message': message,
            }
            await self.channel_layer.group_send(self.group_name, response)
            await self.send(json.dumps(message))
            if status.name == OrderStatus.TRIP_ENDING.name:
                await self.complete()
        else:
            await self.send_error_message(
                {'error': ['Inappropriate order status.']},
            )

    async def make_decision(self, message_info: dict):
        """Обработать принятое решение по заказу."""
        serializer = AnswerSerializer(data=message_info)
        if serializer.is_valid():
            is_agree = serializer.validated_data['is_agree']
            is_relevance = await self.check_order_relevance()
            if is_agree and is_relevance:
                self.is_order_active = True
                self.inactive_order_manager.remove(self.group_name)
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name,
                )
                message = {'message_type': MessageType.DRIVER_DATA.value}
                await self.channel_layer.group_send(
                    self.group_name,
                    {'type': 'chat_message', 'message': message},
                )
                await self.change_status(OrderStatus.DRIVER_ON_THE_WAY)
            else:
                self.inactive_order_manager.free(self.group_name)
                self.driver.add_unsuitable_order(self.group_name)
                if self.driver.is_possible():
                    await self.find_order()
                else:
                    await self.send_error_message(
                        {'error': ['Number of attempts exhausted.']},
                    )
                    await self.complete()
        else:
            await self.send_error_message(serializer.errors)

    async def check_order_relevance(self):
        """Проверка актуальности заказа."""
        if not self.inactive_order_manager.is_exist(self.group_name):
            message = {'message_type': MessageType.NOT_CURRENT_ORDER.value}
            await self.send(text_data=json.dumps(message))
            return False
        return True

    async def cancel(self):
        """Обработка сообщения отмены заказа."""
        if self.is_order_active:
            result = await self.active_order_manager.is_possiple_to_cancel()
            if result:
                message = {'message_type': MessageType.CANCEL.value}
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                    },
                )
                await self.complete()
            else:
                await self.send_error_message(
                    {'error': ['Inappropriate order status.']},
                )
        else:
            await self.complete()

    async def send_error_message(self, errors: dict):
        """Отправить сообщение с ошибками."""
        message = {
            'message_type': MessageType.ERROR.value,
            'info': errors,
        }
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event):
        """Сообщение от клиента."""
        message = event['message']
        message_type = message['message_type']
        if message_type == MessageType.CANCEL.value:
            await self.send(text_data=json.dumps(message))
            await self.complete()

    async def disconnect(self, close_code):
        """Автоматически при отсоединении."""
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def complete(self):
        """Автоматически при отсоединении."""
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )
        await self.close()

# FIXME save order in  model
# get client price
